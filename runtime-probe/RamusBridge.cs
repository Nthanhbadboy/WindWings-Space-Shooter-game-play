// RamusBridge — embedded HTTP probe for Unity (IL2CPP & Mono), loader-agnostic core.
//
// Design goals
//   * Zero external dependencies (no Newtonsoft, no System.Text.Json, no HttpListener).
//   * Raw TcpListener HTTP/1.1 server -> works on Android/CoreCLR where HttpListener is unsupported.
//   * Every Unity API call is marshalled to the main thread (IL2CPP objects are not thread safe).
//   * Works with BepInEx 6 IL2CPP, FusionCore/BepInEx-Android and MelonLoader (see adapters).
//   * Logcat mirror: emits `RAMUSB|{json}` lines so CI can read state even when adb is unavailable
//     (Ramus trial sessions do not expose an adb tunnel).
//
// Endpoints (all JSON, UTF-8)
//   GET  /health                 liveness + scene + fps + timescale
//   GET  /state                  health + device/quality/screen
//   GET  /scene                  active scene + root GameObjects (cap 200)
//   GET  /hierarchy?depth=2&max  recursive tree (node budget)
//   GET  /find?name=Sub&max=50   name search, includes inactive
//   GET  /statics?type=Stage_Datas&max=200
//                                public static primitive fields of a type, via reflection
//   GET  /logs?n=200             ring buffer of Unity log (thread-safe capture)
//   GET  /metrics                frame-time stats + frame count
//   GET  /screenshot             raw image/png from ScreenCapture (<= 6 MB)
//   POST /timescale?v=0.5        Time.timeScale
//   POST /quit                   Application.Quit()
//   POST /mark?name=foo          emits `RAMUSB-MARK|foo` into logcat
//   GET  /wait?scene=Name&timeout=30000
//                                blocks until the active scene matches (CI synchronisation)
//
// Config file (next to the DLL): ramus-bridge.ini
//   port=8080
//   bind=127.0.0.1          # 0.0.0.0 only for trusted lab networks
//   token=                  # when set, require X-Ramus-Token or ?token=
//   mirror=10               # seconds between RAMUSB| log lines, 0 = off
//   statics=true            # enable /statics
//   screenshot=true         # enable /screenshot
// Env vars override: RAMUS_BRIDGE_PORT, RAMUS_BRIDGE_BIND, RAMUS_BRIDGE_TOKEN,
//                    RAMUS_BRIDGE_MIRROR, RAMUS_BRIDGE_STATICS.

using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Ramus.Bridge
{
    // ───────────────────────────────────────────────────────────────────── config

    public sealed class BridgeConfig
    {
        public string Bind = "127.0.0.1";
        public int Port = 8080;
        public string Token = "";
        public int MirrorSeconds = 10;
        public int MirrorRoots = 12;
        public bool EnableStatics = true;
        public bool EnableScreenshot = true;

        public static BridgeConfig Load()
        {
            var c = new BridgeConfig();
            try
            {
                string dir = SafeBaseDir();
                string path = Path.Combine(dir, "ramus-bridge.ini");
                if (File.Exists(path))
                {
                    foreach (var line in File.ReadAllLines(path))
                    {
                        var s = line.Trim();
                        if (s.Length == 0 || s[0] == '#' || s[0] == ';') continue;
                        int eq = s.IndexOf('=');
                        if (eq <= 0) continue;
                        string k = s.Substring(0, eq).Trim().ToLowerInvariant();
                        string v = s.Substring(eq + 1).Trim();
                        switch (k)
                        {
                            case "port": if (int.TryParse(v, out var p)) c.Port = p; break;
                            case "bind": c.Bind = v; break;
                            case "token": c.Token = v; break;
                            case "mirror": if (int.TryParse(v, out var m)) c.MirrorSeconds = m; break;
                            case "mirror_roots": if (int.TryParse(v, out var mr)) c.MirrorRoots = mr; break;
                            case "statics": c.EnableStatics = v != "0" && v.ToLowerInvariant() != "false"; break;
                            case "screenshot": c.EnableScreenshot = v != "0" && v.ToLowerInvariant() != "false"; break;
                        }
                    }
                }
            }
            catch { /* config is best-effort */ }

            c.Port = EnvInt("RAMUS_BRIDGE_PORT", c.Port);
            c.Bind = EnvStr("RAMUS_BRIDGE_BIND", c.Bind);
            c.Token = EnvStr("RAMUS_BRIDGE_TOKEN", c.Token);
            c.MirrorSeconds = EnvInt("RAMUS_BRIDGE_MIRROR", c.MirrorSeconds);
            c.EnableStatics = EnvBool("RAMUS_BRIDGE_STATICS", c.EnableStatics);
            return c;
        }

        static string SafeBaseDir()
        {
            try
            {
                var loc = typeof(BridgeConfig).Assembly.Location;
                if (!string.IsNullOrEmpty(loc)) return Path.GetDirectoryName(loc);
            }
            catch { }
            try { return AppContext.BaseDirectory; } catch { }
            return ".";
        }

        static string EnvStr(string k, string d) { try { var v = Environment.GetEnvironmentVariable(k); return string.IsNullOrEmpty(v) ? d : v; } catch { return d; } }
        static int EnvInt(string k, int d) { var v = Environment.GetEnvironmentVariable(k); return int.TryParse(v, out var x) ? x : d; }
        static bool EnvBool(string k, bool d) { var v = Environment.GetEnvironmentVariable(k); if (string.IsNullOrEmpty(v)) return d; return v != "0" && v.ToLowerInvariant() != "false"; }
    }

    // ───────────────────────────────────────────────────────────────────── logging ring

    public sealed class LogEntry
    {
        public string Time;
        public string Level;
        public string Message;
        public string Stack;
    }

    internal sealed class LogRing
    {
        readonly LogEntry[] _buf;
        int _head, _count;
        readonly object _lock = new object();

        public LogRing(int size) { _buf = new LogEntry[size]; }

        public void Add(LogEntry e)
        {
            lock (_lock)
            {
                _buf[_head] = e;
                _head = (_head + 1) % _buf.Length;
                if (_count < _buf.Length) _count++;
            }
        }

        public List<LogEntry> Tail(int n)
        {
            lock (_lock)
            {
                if (n > _count) n = _count;
                var res = new List<LogEntry>(n);
                int start = (_head - n + _buf.Length) % _buf.Length;
                for (int i = 0; i < n; i++) res.Add(_buf[(start + i) % _buf.Length]);
                return res;
            }
        }
    }

    // ───────────────────────────────────────────────────────────────────── tiny JSON writer

    internal sealed class Jw
    {
        readonly StringBuilder _sb = new StringBuilder(512);
        bool _comma;

        void Sep() { if (_comma) _sb.Append(','); _comma = false; }

        public Jw StartObj() { Sep(); _sb.Append('{'); return this; }
        public Jw EndObj() { _sb.Append('}'); _comma = true; return this; }
        public Jw StartArr() { Sep(); _sb.Append('['); return this; }
        public Jw EndArr() { _sb.Append(']'); _comma = true; return this; }

        public Jw Name(string n) { Sep(); _sb.Append('"').Append(Esc(n)).Append("\":"); return this; }

        public Jw Str(string v) { Sep(); _sb.Append('"').Append(Esc(v)).Append('"'); _comma = true; return this; }
        public Jw Num(double v)
        {
            Sep();
            if (double.IsNaN(v) || double.IsInfinity(v)) _sb.Append('0');
            else _sb.Append(v.ToString("0.####", CultureInfo.InvariantCulture));
            _comma = true; return this;
        }
        public Jw Bool(bool v) { Sep(); _sb.Append(v ? "true" : "false"); _comma = true; return this; }
        public Jw Null() { Sep(); _sb.Append("null"); _comma = true; return this; }
        public Jw Raw(string json) { Sep(); _sb.Append(json); _comma = true; return this; }

        public Jw Prop(string k, string v) { Name(k); return v == null ? Null() : Str(v); }
        public Jw Prop(string k, bool v) { Name(k); return Bool(v); }
        public Jw Prop(string k, double v) { Name(k); return Num(v); }
        public Jw Prop(string k, int v) { Name(k); return Num(v); }

        /// <summary>Writes an already-serialised JSON fragment (array/object) as the value.</summary>
        public Jw PropRaw(string k, string json) { Name(k); return Raw(json); }

        public override string ToString() { return _sb.ToString(); }

        static string Esc(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            var sb = new StringBuilder(s.Length + 8);
            foreach (char ch in s)
            {
                switch (ch)
                {
                    case '"': sb.Append("\\\""); break;
                    case '\\': sb.Append("\\\\"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (ch < 0x20) sb.Append("\\u").Append(((int)ch).ToString("x4"));
                        else sb.Append(ch);
                        break;
                }
            }
            return sb.ToString();
        }
    }

    // ───────────────────────────────────────────────────────────────────── http primitives

    internal sealed class HttpRequest
    {
        public string Method = "GET";
        public string Path = "/";
        public readonly Dictionary<string, string> Query = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        public readonly Dictionary<string, string> Headers = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);
        public string Body = "";
    }

    internal sealed class HttpResponse
    {
        public int Status = 200;
        public string ContentType = "application/json; charset=utf-8";
        public byte[] Body = Array.Empty<byte>();

        public static HttpResponse Json(string json, int status = 200)
        {
            return new HttpResponse { Status = status, Body = Encoding.UTF8.GetBytes(json) };
        }

        public static HttpResponse Error(int status, string message, string detail = null)
        {
            var jw = new Jw().StartObj().Prop("ok", false).Prop("error", message);
            if (!string.IsNullOrEmpty(detail)) jw.Prop("detail", detail);
            jw.EndObj();
            return Json(jw.ToString(), status);
        }
    }

    internal sealed class HttpServer
    {
        readonly TcpListener _listener;
        readonly Action<HttpRequest, HttpResponse> _handler;
        readonly Thread _thread;
        volatile bool _running = true;

        public HttpServer(IPAddress address, int port, Action<HttpRequest, HttpResponse> handler)
        {
            _listener = new TcpListener(address, port);
            _handler = handler;
            _thread = new Thread(AcceptLoop) { IsBackground = true, Name = "ramus-bridge-http" };
        }

        public void Start() { _listener.Start(); _thread.Start(); }

        public void Stop()
        {
            _running = false;
            try { _listener.Stop(); } catch { }
        }

        void AcceptLoop()
        {
            while (_running)
            {
                TcpClient client = null;
                try { client = _listener.AcceptTcpClient(); }
                catch { if (!_running) return; continue; }
                ThreadPool.QueueUserWorkItem(_ => Handle(client));
            }
        }

        void Handle(TcpClient client)
        {
            try
            {
                using (client)
                using (var stream = client.GetStream())
                {
                    client.ReceiveTimeout = 5000;
                    client.SendTimeout = 15000;

                    var req = ReadRequest(stream);
                    if (req == null) return;

                    HttpResponse res;
                    try { res = new HttpResponse(); _handler(req, res); }
                    catch (Exception ex) { res = HttpResponse.Error(500, "handler_exception", ex.GetType().Name + ": " + ex.Message); }

                    WriteResponse(stream, res);
                }
            }
            catch { /* client vanished — never crash the game for a probe */ }
        }

        static HttpRequest ReadRequest(NetworkStream stream)
        {
            var buf = new byte[8192];
            int total = 0;
            int headerEnd = -1;

            while (total < buf.Length)
            {
                int n = stream.Read(buf, total, buf.Length - total);
                if (n <= 0) return null;
                total += n;
                headerEnd = IndexOfHeaderEnd(buf, total);
                if (headerEnd >= 0) break;
            }
            if (headerEnd < 0) return null;

            string head = Encoding.ASCII.GetString(buf, 0, headerEnd);
            var lines = head.Split(new[] { "\r\n" }, StringSplitOptions.None);
            if (lines.Length == 0) return null;

            var first = lines[0].Split(' ');
            if (first.Length < 2) return null;

            var req = new HttpRequest { Method = first[0].ToUpperInvariant() };
            string target = first[1];
            int q = target.IndexOf('?');
            if (q >= 0)
            {
                req.Path = target.Substring(0, q);
                foreach (var pair in target.Substring(q + 1).Split('&'))
                {
                    if (pair.Length == 0) continue;
                    int eq = pair.IndexOf('=');
                    string k = eq < 0 ? pair : pair.Substring(0, eq);
                    string v = eq < 0 ? "" : pair.Substring(eq + 1);
                    try { req.Query[Uri.UnescapeDataString(k)] = Uri.UnescapeDataString(v.Replace("+", " ")); } catch { }
                }
            }
            else req.Path = target;

            for (int i = 1; i < lines.Length; i++)
            {
                int c = lines[i].IndexOf(':');
                if (c <= 0) continue;
                req.Headers[lines[i].Substring(0, c).Trim()] = lines[i].Substring(c + 1).Trim();
            }

            int contentLength = 0;
            if (req.Headers.TryGetValue("Content-Length", out var cl)) int.TryParse(cl, out contentLength);
            contentLength = Math.Min(contentLength, 64 * 1024);

            int bodyStart = headerEnd + 4;
            int already = total - bodyStart;
            if (contentLength > 0)
            {
                var body = new byte[contentLength];
                int copied = Math.Max(0, Math.Min(already, contentLength));
                Array.Copy(buf, bodyStart, body, 0, copied);
                int read = copied;
                while (read < contentLength)
                {
                    int n = stream.Read(body, read, contentLength - read);
                    if (n <= 0) break;
                    read += n;
                }
                req.Body = Encoding.UTF8.GetString(body, 0, read);
            }
            else if (already > 0)
            {
                req.Body = Encoding.UTF8.GetString(buf, bodyStart, already);
            }

            return req;
        }

        static int IndexOfHeaderEnd(byte[] b, int len)
        {
            for (int i = 0; i + 3 < len; i++)
                if (b[i] == 13 && b[i + 1] == 10 && b[i + 2] == 13 && b[i + 3] == 10) return i;
            return -1;
        }

        static void WriteResponse(NetworkStream stream, HttpResponse res)
        {
            var header = new StringBuilder(160);
            header.Append("HTTP/1.1 ").Append(res.Status).Append(' ').Append(Reason(res.Status)).Append("\r\n");
            header.Append("Content-Type: ").Append(res.ContentType).Append("\r\n");
            header.Append("Content-Length: ").Append(res.Body.Length).Append("\r\n");
            header.Append("Cache-Control: no-store\r\n");
            header.Append("Access-Control-Allow-Origin: *\r\n");
            header.Append("Connection: close\r\n\r\n");

            var hb = Encoding.ASCII.GetBytes(header.ToString());
            stream.Write(hb, 0, hb.Length);
            if (res.Body.Length > 0) stream.Write(res.Body, 0, res.Body.Length);
            stream.Flush();
        }

        static string Reason(int s)
        {
            switch (s)
            {
                case 200: return "OK";
                case 400: return "Bad Request";
                case 401: return "Unauthorized";
                case 403: return "Forbidden";
                case 404: return "Not Found";
                case 405: return "Method Not Allowed";
                case 413: return "Payload Too Large";
                case 500: return "Internal Server Error";
                case 503: return "Service Unavailable";
                default: return "OK";
            }
        }
    }

    // ───────────────────────────────────────────────────────────────────── main-thread host

    /// <summary>MonoBehaviour that drains the main-thread queue and mirrors state to logcat.</summary>
    public sealed class BridgeHost : MonoBehaviour
    {
        float _nextMirror;
        float _fpsTimer;
        int _fpsFrames;
        float _fps = -1f;
        string _lastScene;

        public static BridgeHost Create()
        {
            var go = new GameObject("RamusBridgeHost");
            go.hideFlags = HideFlags.HideAndDontSave;
            UnityEngine.Object.DontDestroyOnLoad(go);
            return go.AddComponent<BridgeHost>();
        }

        void Update()
        {
            Bridge.DrainMainQueue();
            Bridge.TrackFrame(Time.unscaledDeltaTime);

            _fpsFrames++;
            _fpsTimer += Time.unscaledDeltaTime;
            if (_fpsTimer >= 0.5f)
            {
                _fps = _fpsFrames / _fpsTimer;
                _fpsFrames = 0;
                _fpsTimer = 0f;
                Bridge.SetFps(_fps);
            }

            // Mirror immediately on a scene change, then on the configured interval.
            string sceneNow = SceneManager.GetActiveScene().name;
            if (sceneNow != _lastScene)
            {
                _lastScene = sceneNow;
                Mirror();
            }
            else if (Bridge.Config.MirrorSeconds > 0 && Time.realtimeSinceStartup >= _nextMirror)
            {
                Mirror();
            }
        }

        void Mirror()
        {
            _nextMirror = Time.realtimeSinceStartup + Mathf.Max(1, Bridge.Config.MirrorSeconds);
            var line = Bridge.CompactStateJson();
            if (line.Length > 3500) line = line.Substring(0, 3500);
            Debug.Log("RAMUSB|" + line);
        }

        void OnApplicationQuit() { Bridge.Shutdown(); }
    }

    // ───────────────────────────────────────────────────────────────────── bridge

    public static class Bridge
    {
        public static BridgeConfig Config { get; private set; }
        public static bool Running { get; private set; }

        static readonly ConcurrentQueue<Action> MainQueue = new ConcurrentQueue<Action>();
        static readonly LogRing Logs = new LogRing(500);
        static readonly float[] FrameTimes = new float[240];

        static HttpServer _server;
        static Action<string> _log;
        static DateTime _startedUtc;
        static int _frameHead, _frameCount;
        static float _fps = -1f;
        static int _mainThreadId = -1;
        static bool _initialised;

        // ── lifecycle

        public static void Init(Action<string> logger)
        {
            if (_initialised) return;
            _initialised = true;
            _log = logger;
            _startedUtc = DateTime.UtcNow;
            _mainThreadId = Thread.CurrentThread.ManagedThreadId;
            Config = BridgeConfig.Load();

            try { Application.logMessageReceivedThreaded += OnLog; } catch { }

            try
            {
                IPAddress addr = Config.Bind == "0.0.0.0" ? IPAddress.Any : IPAddress.Loopback;
                _server = new HttpServer(addr, Config.Port, Probe.Handle);
                _server.Start();
                Running = true;
                Log("listening on http://" + Config.Bind + ":" + Config.Port);
            }
            catch (Exception ex)
            {
                Log("failed to start HTTP server: " + ex.Message);
            }
        }

        public static void Tick() { DrainMainQueue(); }

        public static void Shutdown()
        {
            try { Application.logMessageReceivedThreaded -= OnLog; } catch { }
            if (_server != null) _server.Stop();
            _server = null;
            Running = false;
        }

        static void Log(string msg)
        {
            try { _log?.Invoke("[RamusBridge] " + msg); } catch { }
            try { Debug.Log("[RamusBridge] " + msg); } catch { }
        }

        // ── thread marshalling

        public static T OnMain<T>(Func<T> fn, int timeoutMs = 5000)
        {
            if (Thread.CurrentThread.ManagedThreadId == _mainThreadId) return fn();

            var tcs = new TaskCompletionSource<T>(TaskCreationOptions.RunContinuationsAsynchronously);
            MainQueue.Enqueue(() =>
            {
                try { tcs.TrySetResult(fn()); }
                catch (Exception ex) { tcs.TrySetException(ex); }
            });

            if (!tcs.Task.Wait(timeoutMs))
                throw new TimeoutException("main thread did not answer within " + timeoutMs + " ms");
            return tcs.Task.Result;
        }

        public static void OnMain(Action fn, int timeoutMs = 5000) { OnMain<bool>(() => { fn(); return true; }, timeoutMs); }

        public static void DrainMainQueue()
        {
            int budget = 64;
            while (budget-- > 0 && MainQueue.TryDequeue(out var action))
            {
                try { action(); } catch (Exception ex) { Log("queued action failed: " + ex.Message); }
            }
        }

        // ── metrics

        public static void TrackFrame(float dt)
        {
            FrameTimes[_frameHead] = dt;
            _frameHead = (_frameHead + 1) % FrameTimes.Length;
            if (_frameCount < FrameTimes.Length) _frameCount++;
        }

        public static void SetFps(float fps) { _fps = fps; }

        public static float Fps => _fps;

        public static double AvgFrameMs()
        {
            if (_frameCount == 0) return 0;
            double sum = 0;
            for (int i = 0; i < _frameCount; i++) sum += FrameTimes[i];
            return 1000.0 * sum / _frameCount;
        }

        public static double MaxFrameMs()
        {
            double max = 0;
            for (int i = 0; i < _frameCount; i++) if (FrameTimes[i] > max) max = FrameTimes[i];
            return max * 1000.0;
        }

        // ── logging

        static void OnLog(string condition, string stackTrace, LogType type)
        {
            var e = new LogEntry
            {
                Time = DateTime.UtcNow.ToString("HH:mm:ss.fff", CultureInfo.InvariantCulture),
                Level = type.ToString(),
                Message = condition != null && condition.Length > 2000 ? condition.Substring(0, 2000) : condition,
                Stack = FirstLine(stackTrace)
            };
            Logs.Add(e);
        }

        static string FirstLine(string s)
        {
            if (string.IsNullOrEmpty(s)) return "";
            int i = s.IndexOf('\n');
            var line = i < 0 ? s : s.Substring(0, i);
            return line.Length > 300 ? line.Substring(0, 300) : line;
        }

        public static List<LogEntry> TailLogs(int n) { return Logs.Tail(n); }

        // ── state snapshots (must run on main thread)

        public static string CompactStateJson()
        {
            return OnMain(() =>
            {
                var sc = SceneManager.GetActiveScene();
                var roots = sc.GetRootGameObjects();
                var jw = new Jw().StartObj()
                    .Prop("ok", true)
                    .Prop("scene", sc.name)
                    .Prop("frame", Time.frameCount)
                    .Prop("fps", _fps < 0 ? 0 : _fps)
                    .Prop("ts", Time.timeScale)
                    .Prop("uptime", (DateTime.UtcNow - _startedUtc).TotalSeconds)
                    .Prop("unity", Application.unityVersion)
                    .Prop("rootCount", roots.Length);

                // Root names travel through logcat so a trial session (no adb) still
                // sees the scene structure, not just the scene name.
                int limit = Math.Min(roots.Length, Math.Max(0, Config.MirrorRoots));
                if (limit > 0)
                {
                    jw.Name("roots").StartArr();
                    for (int i = 0; i < limit; i++)
                    {
                        var go = roots[i];
                        if (go == null) continue;
                        jw.StartObj().Prop("n", go.name).Prop("a", go.activeSelf).EndObj();
                    }
                    jw.EndArr();
                }

                jw.EndObj();
                return jw.ToString();
            }, 2000);
        }

        public static string HealthJson()
        {
            return OnMain(() =>
            {
                var sc = SceneManager.GetActiveScene();
                return new Jw().StartObj()
                    .Prop("ok", true)
                    .Prop("pid", SafePid())
                    .Prop("uptime", (DateTime.UtcNow - _startedUtc).TotalSeconds)
                    .Prop("scene", sc.name)
                    .Prop("scenePath", sc.path)
                    .Prop("sceneBuildIndex", sc.buildIndex)
                    .Prop("sceneCount", SceneManager.sceneCount)
                    .Prop("frame", Time.frameCount)
                    .Prop("fps", _fps < 0 ? 0 : _fps)
                    .Prop("avgFrameMs", AvgFrameMs())
                    .Prop("maxFrameMs", MaxFrameMs())
                    .Prop("timeScale", Time.timeScale)
                    .Prop("realtime", Time.realtimeSinceStartup)
                    .Prop("unity", Application.unityVersion)
                    .Prop("platform", Application.platform.ToString())
                    .Prop("playing", Application.isPlaying)
                    .EndObj().ToString();
            });
        }

        public static string StateJson()
        {
            return OnMain(() =>
            {
                var sc = SceneManager.GetActiveScene();
                return new Jw().StartObj()
                    .Prop("ok", true)
                    .Prop("scene", sc.name)
                    .Prop("frame", Time.frameCount)
                    .Prop("fps", _fps < 0 ? 0 : _fps)
                    .Prop("timeScale", Time.timeScale)
                    .Prop("screenW", Screen.width)
                    .Prop("screenH", Screen.height)
                    .Prop("dpi", Screen.dpi)
                    .Prop("fullscreen", Screen.fullScreen)
                    .Prop("quality", QualitySettings.names.Length > 0 ? QualitySettings.names[QualitySettings.GetQualityLevel()] : "")
                    .Prop("vSync", QualitySettings.vSyncCount)
                    .Prop("targetFrameRate", Application.targetFrameRate)
                    .Prop("device", SystemInfo.deviceModel)
                    .Prop("os", SystemInfo.operatingSystem)
                    .Prop("processorCount", SystemInfo.processorCount)
                    .Prop("systemMemoryMB", SystemInfo.systemMemorySize)
                    .Prop("graphics", SystemInfo.graphicsDeviceName)
                    .Prop("gcMB", GC.GetTotalMemory(false) / 1048576.0)
                    .EndObj().ToString();
            });
        }

        public static string SceneJson(int maxRoots)
        {
            return OnMain(() =>
            {
                var sc = SceneManager.GetActiveScene();
                var roots = sc.GetRootGameObjects();
                var jw = new Jw().StartObj()
                    .Prop("ok", true)
                    .Prop("name", sc.name)
                    .Prop("path", sc.path)
                    .Prop("buildIndex", sc.buildIndex)
                    .Prop("isLoaded", sc.isLoaded)
                    .Prop("rootCount", roots.Length)
                    .Name("roots").StartArr();

                int count = Math.Min(roots.Length, Math.Max(0, maxRoots));
                for (int i = 0; i < count; i++)
                {
                    var go = roots[i];
                    if (go == null) continue;
                    jw.StartObj()
                      .Prop("name", go.name)
                      .Prop("active", go.activeSelf)
                      .Prop("tag", SafeTag(go))
                      .Prop("layer", go.layer)
                      .Prop("children", go.transform != null ? go.transform.childCount : 0)
                      .Prop("pos", Vec(go.transform != null ? go.transform.position : Vector3.zero))
                      .PropRaw("components", Components(go, 10))
                      .EndObj();
                }

                jw.EndArr().EndObj();
                return jw.ToString();
            });
        }

        public static string HierarchyJson(int depth, int max)
        {
            return OnMain(() =>
            {
                var sc = SceneManager.GetActiveScene();
                var roots = sc.GetRootGameObjects();
                var jw = new Jw().StartObj().Prop("ok", true).Prop("scene", sc.name).Name("tree").StartArr();
                int budget = Math.Max(1, max);
                foreach (var go in roots)
                {
                    if (budget <= 0) break;
                    WriteNode(jw, go, 0, Math.Max(0, depth), ref budget);
                }
                jw.EndArr().EndObj();
                return jw.ToString();
            });
        }

        static void WriteNode(Jw jw, GameObject go, int level, int maxDepth, ref int budget)
        {
            if (go == null || budget <= 0) return;
            budget--;

            jw.StartObj()
              .Prop("name", go.name)
              .Prop("active", go.activeSelf)
              .Prop("level", level)
              .PropRaw("components", Components(go, 6));

            if (level < maxDepth && go.transform != null && go.transform.childCount > 0)
            {
                jw.Name("children").StartArr();
                for (int i = 0; i < go.transform.childCount && budget > 0; i++)
                    WriteNode(jw, go.transform.GetChild(i).gameObject, level + 1, maxDepth, ref budget);
                jw.EndArr();
            }

            jw.EndObj();
        }

        public static string FindJson(string needle, int max)
        {
            return OnMain(() =>
            {
                var sc = SceneManager.GetActiveScene();
                var roots = sc.GetRootGameObjects();
                var hits = new List<GameObject>();
                int budget = 20000;

                foreach (var r in roots)
                {
                    if (hits.Count >= max || budget <= 0) break;
                    Search(r.transform, needle, max, ref budget, hits);
                }

                var jw = new Jw().StartObj().Prop("ok", true).Prop("query", needle).Prop("count", hits.Count).Name("objects").StartArr();
                foreach (var go in hits)
                {
                    jw.StartObj()
                      .Prop("name", go.name)
                      .Prop("path", PathOf(go.transform))
                      .Prop("active", go.activeSelf)
                      .Prop("activeInHierarchy", go.activeInHierarchy)
                      .Prop("tag", SafeTag(go))
                      .Prop("layer", go.layer)
                      .Prop("pos", Vec(go.transform.position))
                      .PropRaw("components", Components(go, 12))
                      .EndObj();
                }
                jw.EndArr().EndObj();
                return jw.ToString();
            });
        }

        static void Search(Transform t, string needle, int max, ref int budget, List<GameObject> hits)
        {
            if (t == null) return;
            budget--;
            if (budget <= 0 || hits.Count >= max) return;

            var go = t.gameObject;
            if (go != null && go.name != null && go.name.IndexOf(needle, StringComparison.OrdinalIgnoreCase) >= 0)
                hits.Add(go);

            int n = t.childCount;
            for (int i = 0; i < n; i++)
            {
                if (budget <= 0 || hits.Count >= max) return;
                Search(t.GetChild(i), needle, max, ref budget, hits);
            }
        }

        public static string StaticsJson(string typeName, int max)
        {
            return OnMain(() =>
            {
                if (!Config.EnableStatics)
                    return new Jw().StartObj().Prop("ok", false).Prop("error", "statics_disabled").EndObj().ToString();

                Type type = ResolveType(typeName);
                if (type == null)
                    return new Jw().StartObj().Prop("ok", false).Prop("error", "type_not_found").Prop("type", typeName).EndObj().ToString();

                var jw = new Jw().StartObj().Prop("ok", true).Prop("type", type.FullName).Name("fields").StartObj();
                int written = 0;
                FieldInfo[] fields;
                try { fields = type.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static); }
                catch (Exception ex)
                {
                    return new Jw().StartObj().Prop("ok", false).Prop("error", "reflection_failed").Prop("detail", ex.Message).EndObj().ToString();
                }

                foreach (var f in fields)
                {
                    if (written >= max) break;
                    try
                    {
                        object v = f.GetValue(null);
                        if (v == null) { jw.Name(f.Name).Null(); written++; continue; }

                        var t = v.GetType();
                        if (t == typeof(string)) jw.Name(f.Name).Str((string)v);
                        else if (t == typeof(bool)) jw.Name(f.Name).Bool((bool)v);
                        else if (t == typeof(int) || t == typeof(long) || t == typeof(short) || t == typeof(byte))
                            jw.Name(f.Name).Num(Convert.ToDouble(v, CultureInfo.InvariantCulture));
                        else if (t == typeof(float) || t == typeof(double) || t == typeof(decimal))
                            jw.Name(f.Name).Num(Convert.ToDouble(v, CultureInfo.InvariantCulture));
                        else if (v is Array arr && arr.Rank == 1 && arr.Length <= 64)
                        {
                            jw.Name(f.Name).StartArr();
                            foreach (var item in arr)
                            {
                                if (item == null) jw.Null();
                                else if (item is string s2) jw.Str(s2);
                                else if (item is bool b2) jw.Bool(b2);
                                else if (item is IConvertible c2 && (item is int || item is long || item is float || item is double || item is short || item is byte))
                                    jw.Num(c2.ToDouble(CultureInfo.InvariantCulture));
                                else jw.Str(item.ToString());
                            }
                            jw.EndArr();
                        }
                        else jw.Name(f.Name).Str("(" + t.Name + ")");
                        written++;
                    }
                    catch { /* skip fields that interop refuses to read */ }
                }

                jw.EndObj().Prop("written", written).EndObj();
                return jw.ToString();
            }, 6000);
        }

        static Type ResolveType(string name)
        {
            if (string.IsNullOrEmpty(name)) return null;
            try
            {
                var direct = Type.GetType(name, false);
                if (direct != null) return direct;

                foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
                {
                    try
                    {
                        var t = asm.GetType(name, false);
                        if (t != null) return t;

                        foreach (var candidate in asm.GetTypes())
                        {
                            if (candidate == null) continue;
                            if (candidate.Name == name)
                            {
                                // Prefer the game assembly when several types share a simple name.
                                if (asm.GetName().Name.IndexOf("Assembly-CSharp", StringComparison.OrdinalIgnoreCase) >= 0) return candidate;
                                if (candidate.FullName == name) return candidate;
                            }
                        }
                    }
                    catch { }
                }

                foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
                {
                    try
                    {
                        foreach (var candidate in asm.GetTypes())
                            if (candidate != null && candidate.Name == name) return candidate;
                    }
                    catch { }
                }
            }
            catch { }
            return null;
        }

        public static string LogsJson(int n)
        {
            var entries = TailLogs(n);
            var jw = new Jw().StartObj().Prop("ok", true).Prop("count", entries.Count).Name("logs").StartArr();
            foreach (var e in entries)
            {
                jw.StartObj()
                  .Prop("t", e.Time)
                  .Prop("level", e.Level)
                  .Prop("msg", e.Message)
                  .Prop("stack", e.Stack)
                  .EndObj();
            }
            jw.EndArr().EndObj();
            return jw.ToString();
        }

        internal static HttpResponse Screenshot()
        {
            if (!Config.EnableScreenshot)
                return HttpResponse.Error(403, "screenshot_disabled");

            return OnMain<HttpResponse>(() =>
            {
                Texture2D tex = null;
                try
                {
                    tex = ScreenCapture.CaptureScreenshotAsTexture();
                    if (tex == null) return HttpResponse.Error(503, "capture_failed", "ScreenCapture returned null");
                    byte[] png = ImageConversion.EncodeToPNG(tex);
                    if (png == null || png.Length == 0) return HttpResponse.Error(503, "encode_failed");
                    if (png.Length > 6 * 1024 * 1024)
                        return HttpResponse.Error(413, "screenshot_too_large", "use ramus screenshot for large frames");

                    return new HttpResponse { ContentType = "image/png", Body = png };
                }
                catch (Exception ex)
                {
                    return HttpResponse.Error(500, "screenshot_exception", ex.Message);
                }
                finally
                {
                    if (tex != null) UnityEngine.Object.Destroy(tex);
                }
            }, 8000);
        }

        public static string WaitScene(string name, int timeoutMs)
        {
            var started = DateTime.UtcNow;
            while ((DateTime.UtcNow - started).TotalMilliseconds < timeoutMs)
            {
                string current = OnMain(() => SceneManager.GetActiveScene().name, 2000);
                if (string.Equals(current, name, StringComparison.OrdinalIgnoreCase))
                    return new Jw().StartObj().Prop("ok", true).Prop("scene", current)
                        .Prop("waitedMs", (DateTime.UtcNow - started).TotalMilliseconds).EndObj().ToString();
                Thread.Sleep(250);
            }

            string last = OnMain(() => SceneManager.GetActiveScene().name, 2000);
            return new Jw().StartObj().Prop("ok", false).Prop("error", "timeout")
                .Prop("expected", name).Prop("scene", last)
                .Prop("waitedMs", (DateTime.UtcNow - started).TotalMilliseconds).EndObj().ToString();
        }

        // ── helpers

        static string SafePid()
        {
            try { return System.Diagnostics.Process.GetCurrentProcess().Id.ToString(CultureInfo.InvariantCulture); }
            catch { return ""; }
        }

        static string SafeTag(GameObject go)
        {
            try { return go.tag; } catch { return ""; }
        }

        static string Vec(Vector3 v)
        {
            return v.x.ToString("0.##", CultureInfo.InvariantCulture) + ","
                 + v.y.ToString("0.##", CultureInfo.InvariantCulture) + ","
                 + v.z.ToString("0.##", CultureInfo.InvariantCulture);
        }

        static string Components(GameObject go, int max)
        {
            var jw = new Jw().StartArr();
            try
            {
                var comps = go.GetComponents<Component>();
                int n = Math.Min(comps.Length, max);
                for (int i = 0; i < n; i++)
                {
                    var c = comps[i];
                    if (c == null) jw.Str("(missing)");
                    else
                    {
                        try { jw.Str(c.GetType().Name); }
                        catch { jw.Str("(interop)"); }
                    }
                }
                if (comps.Length > max) jw.Str("+" + (comps.Length - max));
            }
            catch { }
            jw.EndArr();
            return jw.ToString();
        }

        static string PathOf(Transform t)
        {
            try
            {
                var parts = new List<string>(8);
                while (t != null) { parts.Add(t.name); t = t.parent; }
                parts.Reverse();
                return string.Join("/", parts.ToArray());
            }
            catch { return ""; }
        }

        public static void SetTimeScale(float v)
        {
            OnMain(() => { Time.timeScale = v; });
        }

        public static void RequestQuit()
        {
            try { OnMain(() => Application.Quit(), 1000); } catch { }
            try { Application.Quit(); } catch { }
        }
    }

    // ───────────────────────────────────────────────────────────────────── router

    internal static class Probe
    {
        public static void Handle(HttpRequest req, HttpResponse res)
        {
            try
            {
                if (!Authorised(req)) { Copy(res, HttpResponse.Error(401, "unauthorized")); return; }

                switch (req.Method + " " + req.Path)
                {
                    case "GET /health":
                        Copy(res, HttpResponse.Json(Bridge.HealthJson()));
                        return;

                    case "GET /state":
                        Copy(res, HttpResponse.Json(Bridge.StateJson()));
                        return;

                    case "GET /scene":
                        Copy(res, HttpResponse.Json(Bridge.SceneJson(Q(req, "max", 200))));
                        return;

                    case "GET /hierarchy":
                        Copy(res, HttpResponse.Json(Bridge.HierarchyJson(Q(req, "depth", 2), Q(req, "max", 800))));
                        return;

                    case "GET /find":
                        Copy(res, HttpResponse.Json(Bridge.FindJson(req.Query.TryGetValue("name", out var n) ? n : "", Q(req, "max", 50))));
                        return;

                    case "GET /statics":
                        Copy(res, HttpResponse.Json(Bridge.StaticsJson(req.Query.TryGetValue("type", out var t) ? t : "", Q(req, "max", 200))));
                        return;

                    case "GET /logs":
                        Copy(res, HttpResponse.Json(Bridge.LogsJson(Q(req, "n", 200))));
                        return;

                    case "GET /metrics":
                        Copy(res, HttpResponse.Json(new Jw().StartObj()
                            .Prop("ok", true)
                            .Prop("fps", Bridge.Fps < 0 ? 0 : Bridge.Fps)
                            .Prop("avgFrameMs", Bridge.AvgFrameMs())
                            .Prop("maxFrameMs", Bridge.MaxFrameMs())
                            .EndObj().ToString()));
                        return;

                    case "GET /screenshot":
                        Copy(res, Bridge.Screenshot());
                        return;

                    case "POST /timescale":
                        Bridge.SetTimeScale((float)Q(req, "v", 1.0));
                        Copy(res, HttpResponse.Json(new Jw().StartObj().Prop("ok", true).Prop("timeScale", Q(req, "v", 1.0)).EndObj().ToString()));
                        return;

                    case "POST /quit":
                        Copy(res, HttpResponse.Json(new Jw().StartObj().Prop("ok", true).Prop("bye", true).EndObj().ToString()));
                        Bridge.RequestQuit();
                        return;

                    case "POST /mark":
                        string mark = req.Query.TryGetValue("name", out var m) ? m : "mark";
                        try { Debug.Log("RAMUSB-MARK|" + mark); } catch { }
                        Copy(res, HttpResponse.Json(new Jw().StartObj().Prop("ok", true).Prop("mark", mark).EndObj().ToString()));
                        return;

                    case "GET /wait":
                        string scene = req.Query.TryGetValue("scene", out var s) ? s : "";
                        int timeout = Q(req, "timeout", 30000);
                        Copy(res, HttpResponse.Json(Bridge.WaitScene(scene, Math.Min(timeout, 180000))));
                        return;

                    case "GET /":
                        Copy(res, HttpResponse.Json(IndexJson()));
                        return;
                }

                Copy(res, HttpResponse.Error(404, "not_found", req.Method + " " + req.Path));
            }
            catch (Exception ex)
            {
                Copy(res, HttpResponse.Error(500, "probe_exception", ex.GetType().Name + ": " + ex.Message));
            }
        }

        static void Copy(HttpResponse dst, HttpResponse src)
        {
            dst.Status = src.Status;
            dst.ContentType = src.ContentType;
            dst.Body = src.Body;
        }

        static bool Authorised(HttpRequest req)
        {
            string token = Bridge.Config != null ? Bridge.Config.Token : "";
            if (string.IsNullOrEmpty(token)) return true;

            if (req.Headers.TryGetValue("X-Ramus-Token", out var h) && h == token) return true;
            if (req.Query.TryGetValue("token", out var q) && q == token) return true;
            return false;
        }

        static int Q(HttpRequest req, string key, int fallback)
        {
            if (req.Query.TryGetValue(key, out var raw) && int.TryParse(raw, out var v)) return v;
            return fallback;
        }

        static double Q(HttpRequest req, string key, double fallback)
        {
            if (req.Query.TryGetValue(key, out var raw) && double.TryParse(raw, NumberStyles.Float, CultureInfo.InvariantCulture, out var v)) return v;
            return fallback;
        }

        static string IndexJson()
        {
            var jw = new Jw().StartObj().Prop("ok", true).Prop("name", "ramus-bridge").Prop("version", "1.0.0");
            jw.Name("endpoints").StartArr()
              .Str("GET /health").Str("GET /state").Str("GET /scene").Str("GET /hierarchy?depth=2&max=800")
              .Str("GET /find?name=Sub").Str("GET /statics?type=Stage_Datas").Str("GET /logs?n=200")
              .Str("GET /metrics").Str("GET /screenshot").Str("POST /timescale?v=1")
              .Str("POST /quit").Str("POST /mark?name=x").Str("GET /wait?scene=Name&timeout=30000")
              .EndArr().EndObj();
            return jw.ToString();
        }
    }
}
