// RamusBridge â€” embedded HTTP probe for Unity (IL2CPP & Mono), loader-agnostic core.
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
    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ config

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

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ logging ring

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

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ tiny JSON writer

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
        public Jw Prop(string k, long v) { Name(k); return Num(v); }

        /// <summary>Dynamic-dispatch overload used with the Safe() fallback
        /// helper: value type decides the JSON form at runtime.</summary>
        public Jw PropObj(string k, object v)
        {
            Name(k);
            if (v == null) return Null();
            if (v is bool b) return Bool(b);
            if (v is int i) return Num(i);
            if (v is long l) return Num(l);
            if (v is double d) return Num(d);
            if (v is float f) return Num(f);
            return Str(v.ToString());
        }

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

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ http primitives

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
            catch { /* client vanished â€” never crash the game for a probe */ }
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

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ main-thread host

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

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ bridge

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

        // â”€â”€ lifecycle

        public static void Init(Action<string> logger)
        {
            if (_initialised) return;
            _initialised = true;
            _log = logger;
            _startedUtc = DateTime.UtcNow;
            _mainThreadId = Thread.CurrentThread.ManagedThreadId;
            Config = BridgeConfig.Load();

            AttachLogCapture();

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
            DetachLogCapture();
            if (_server != null) _server.Stop();
            _server = null;
            Running = false;
        }

        // â”€â”€ log capture
        // Bind Application.logMessageReceived(Threaded) through reflection so
        // the file also compiles against Il2CppInterop proxies that may expose
        // only a subset of Unity events. Mismatch just disables the capture.
        static Delegate _logDelegate;

        public static void AttachLogCapture()
        {
            try
            {
                var appType = typeof(Application);
                var ev = appType.GetEvent("logMessageReceivedThreaded") ?? appType.GetEvent("logMessageReceived");
                if (ev == null) { Log("log capture: no Application event exposed"); return; }
                var m = typeof(Bridge).GetMethod("OnLog", BindingFlags.NonPublic | BindingFlags.Static);
                _logDelegate = Delegate.CreateDelegate(ev.EventHandlerType, m);
                ev.AddEventHandler(null, _logDelegate);
                Log("log capture attached via " + ev.Name);
            }
            catch (Exception ex) { Log("log capture attach failed: " + ex.Message); }
        }

        public static void DetachLogCapture()
        {
            try
            {
                if (_logDelegate == null) return;
                var ev = typeof(Application).GetEvent("logMessageReceivedThreaded")
                         ?? typeof(Application).GetEvent("logMessageReceived");
                ev?.RemoveEventHandler(null, _logDelegate);
                _logDelegate = null;
            }
            catch { }
        }

        static void Log(string msg)
        {
            try { _log?.Invoke("[RamusBridge] " + msg); } catch { }
            try { Debug.Log("[RamusBridge] " + msg); } catch { }
        }

        // â”€â”€ thread marshalling

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

        // â”€â”€ metrics

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

        // â”€â”€ logging

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

        // â”€â”€ state snapshots (must run on main thread)

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
                    .Prop("scenePath", sc.name)
                    .PropObj("sceneBuildIndex", Safe(() => sc.buildIndex, -1))
                    .PropObj("sceneCount", Safe(() => SceneManager.sceneCount, -1))
                    .Prop("frame", Time.frameCount)
                    .Prop("fps", _fps < 0 ? 0 : _fps)
                    .Prop("avgFrameMs", AvgFrameMs())
                    .Prop("maxFrameMs", MaxFrameMs())
                    .Prop("timeScale", Time.timeScale)
                    .Prop("realtime", Time.realtimeSinceStartup)
                    .Prop("unity", Application.unityVersion)
                    .PropObj("platform", Safe(() => Application.platform.ToString(), "?"))
                    .PropObj("playing", Safe(() => Application.isPlaying, false))
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
                    .PropObj("screenW", Safe(() => Screen.width, -1))
                    .PropObj("screenH", Safe(() => Screen.height, -1))
                    .PropObj("dpi", Safe(() => Screen.dpi, -1.0))
                    .PropObj("fullscreen", Safe(() => Screen.fullScreen, false))
                    .PropObj("quality", Safe(() => (QualitySettings.names.Length > 0 ? QualitySettings.names[QualitySettings.GetQualityLevel()] : ""), ""))
                    .PropObj("vSync", Safe(() => QualitySettings.vSyncCount, -1))
                    .PropObj("targetFrameRate", Safe(() => Application.targetFrameRate, -1))
                    .PropObj("device", Safe(() => SystemInfo.deviceModel, "?"))
                    .PropObj("os", Safe(() => SystemInfo.operatingSystem, "?"))
                    .PropObj("processorCount", Safe(() => SystemInfo.processorCount, -1))
                    .PropObj("systemMemoryMB", Safe(() => SystemInfo.systemMemorySize, -1))
                    .PropObj("graphics", Safe(() => SystemInfo.graphicsDeviceName, "?"))
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
                    .Prop("path", sc.name)
                    .PropObj("buildIndex", Safe(() => sc.buildIndex, -1))
                    .PropObj("isLoaded", Safe(() => sc.isLoaded, true))
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

        /// <summary>GET /anim — what is actually playing right now.
        ///
        /// Every animation conclusion in docs/ so far is offline: it comes from
        /// asset names and asm, never from a running game. This reads the live
        /// state so "Boss uses Attack3" becomes a measurement instead of an
        /// inference. Spine types are not referenced at compile time (the stub
        /// build has no Spine at all), so both Spine and Animator are read
        /// through reflection — the same file then compiles for every target.
        /// </summary>
        public static string AnimJson(string nameFilter, int max)
        {
            return OnMain(() => AnimJsonFrom(nameFilter, max, null), 8000);
        }

        /// <summary>Same as AnimJson but walks the supplied roots. The scene is
        /// empty in the stub build, so the self-test needs a way in without
        /// reaching into SceneManager.</summary>
        public static string AnimJsonFrom(string nameFilter, int max, GameObject[] explicitRoots)
        {
            {
                var jw = new Jw().StartObj().Prop("ok", true);
                if (!string.IsNullOrEmpty(nameFilter)) jw.Prop("filter", nameFilter);

                var items = new List<string>();
                int scanned = 0, budget = 20000;

                try
                {
                    var roots = explicitRoots ?? SceneManager.GetActiveScene().GetRootGameObjects();
                    foreach (var root in roots)
                    {
                        if (root == null) continue;
                        if (items.Count >= max || budget <= 0) break;
                        WalkAnim(root.transform, nameFilter, max, items, ref scanned, ref budget);
                    }
                }
                catch (Exception ex)
                {
                    return new Jw().StartObj().Prop("ok", false).Prop("error", "scene_walk_failed")
                        .Prop("detail", ex.Message).EndObj().ToString();
                }

                jw.Prop("count", items.Count).Prop("scanned", scanned)
                  .Name("items").StartArr();
                foreach (var one in items) jw.Raw(one);
                jw.EndArr().EndObj();
                return jw.ToString();
            }
        }

        static void WalkAnim(Transform t, string filter, int max, List<string> items,
                             ref int scanned, ref int budget)
        {
            if (t == null) return;
            budget--;
            if (budget <= 0 || items.Count >= max) return;
            scanned++;

            var go = SafeGameObject(t);
            if (go != null)
            {
                bool match = string.IsNullOrEmpty(filter) ||
                             (go.name != null && go.name.IndexOf(filter, StringComparison.OrdinalIgnoreCase) >= 0);

                if (match)
                {
                    string desc = DescribeAnimation(go);
                    if (desc != null) items.Add(desc);
                }
            }

            int n = 0;
            try { n = t.childCount; } catch { n = 0; }
            for (int i = 0; i < n; i++)
            {
                if (budget <= 0 || items.Count >= max) return;
                Transform child = null;
                try { child = t.GetChild(i); } catch { }
                WalkAnim(child, filter, max, items, ref scanned, ref budget);
            }
        }

        static GameObject SafeGameObject(Transform t)
        {
            try { return t.gameObject; } catch { return null; }
        }

        /// <summary>One JSON object describing what this GameObject is playing, or
        /// null when it has no animation component at all.</summary>
        static string DescribeAnimation(GameObject go)
        {
            // Generic overload first: that is the one Components() already uses,
            // and it is the one proven against il2cpp interop proxies on device.
            Component[] comps;
            try { comps = go.GetComponents<Component>(); }
            catch
            {
                try { comps = go.GetComponents(typeof(Component)); }
                catch { return null; }
            }
            if (comps == null) return null;

            foreach (var c in comps)
            {
                if (c == null) continue;
                string tn;
                try { tn = c.GetType().Name; } catch { continue; }

                if (tn == "SkeletonAnimation" || tn == "SkeletonGraphic" || tn == "SkeletonRenderer")
                    return SpineDesc(go, c, tn);
                if (tn == "Animator" || tn == "Animation")
                    return AnimatorDesc(go, c, tn);
            }
            return null;
        }

        static string SpineDesc(GameObject go, Component c, string typeName)
        {
            var jw = new Jw().StartObj()
                .Prop("go", SafeName(go))
                .Prop("path", PathOf(go.transform))
                .Prop("kind", "spine").Prop("component", typeName);

            // SkeletonAnimation exposes AnimationName directly; the track entry
            // carries the clock. Either alone is weak: the name says what was
            // asked for, the time says whether it is advancing.
            var animName = ReadMember(c, "AnimationName") as string;
            if (animName != null) jw.Prop("anim", trunc(animName));

            var state = ReadMember(c, "state") ?? ReadMember(c, "State");
            var entry = TrackEntry(state, 0);
            if (entry != null)
            {
                var t = NumOf(ReadMember(entry, "Time"));
                if (!double.IsNaN(t)) jw.Prop("time", t);
                var loop = ReadMember(entry, "Loop");
                if (loop is bool lb) jw.Prop("loop", lb);
                var anim = ReadMember(entry, "Animation");
                var nm = anim == null ? null : ReadMember(anim, "Name") as string;
                if (nm != null) jw.Prop("entryAnim", trunc(nm));
                var end = NumOf(ReadMember(entry, "AnimationEnd"));
                if (!double.IsNaN(end)) jw.Prop("length", end);
            }

            var ts = NumOf(ReadMember(c, "timeScale"));
            if (!double.IsNaN(ts)) jw.Prop("timeScale", ts);

            return jw.EndObj().ToString();
        }

        static object TrackEntry(object state, int track)
        {
            if (state == null) return null;
            try
            {
                var m = state.GetType().GetMethod("GetCurrent", new[] { typeof(int) });
                if (m == null) return null;
                return m.Invoke(state, new object[] { track });
            }
            catch { return null; }
        }

        static string AnimatorDesc(GameObject go, Component c, string typeName)
        {
            var jw = new Jw().StartObj()
                .Prop("go", SafeName(go))
                .Prop("path", PathOf(go.transform))
                .Prop("kind", typeName == "Animation" ? "legacy" : "animator").Prop("component", typeName);

            var speed = NumOf(ReadMember(c, "speed"));
            if (!double.IsNaN(speed)) jw.Prop("speed", speed);

            // AnimatorStateInfo is a struct returned by value; reflection gives a
            // boxed copy and its fields are still readable.
            object info = null;
            try
            {
                var m = c.GetType().GetMethod("GetCurrentAnimatorStateInfo", new[] { typeof(int) });
                if (m != null) info = m.Invoke(c, new object[] { 0 });
            }
            catch { }

            if (info != null)
            {
                var norm = NumOf(ReadMember(info, "normalizedTime"));
                if (!double.IsNaN(norm)) jw.Prop("normalized", norm);
                var len = NumOf(ReadMember(info, "length"));
                if (!double.IsNaN(len)) jw.Prop("length", len);
                var loop = ReadMember(info, "loop");
                if (loop is bool lb) jw.Prop("loop", lb);
                if (!double.IsNaN(norm) && !double.IsNaN(len)) jw.Prop("time", norm * len);
            }

            // The state machine reports hashes; the clip list is the readable name.
            string clip = null;
            try
            {
                var m = c.GetType().GetMethod("GetCurrentAnimatorClipInfo", new[] { typeof(int) });
                if (m != null)
                {
                    var arr = m.Invoke(c, new object[] { 0 }) as Array;
                    if (arr != null && arr.Length > 0)
                    {
                        var ci = arr.GetValue(0);
                        var clipObj = ReadMember(ci, "clip");
                        if (clipObj != null) clip = ReadMember(clipObj, "name") as string;
                    }
                }
            }
            catch { }

            if (clip != null) jw.Prop("clip", trunc(clip));
            return jw.EndObj().ToString();
        }

        static string SafeName(GameObject go)
        {
            try { return go.name; } catch { return null; }
        }

        /// <summary>Property first, then field, on the runtime type and its bases.
        /// Interop proxies expose some members only one of the two ways.</summary>
        static object ReadMember(object obj, string member)
        {
            if (obj == null || member == null) return null;
            try
            {
                var t = obj.GetType();
                var p = t.GetProperty(member, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                if (p != null && p.GetIndexParameters().Length == 0)
                {
                    try { return p.GetValue(obj, null); } catch { }
                }
                var f = t.GetField(member, BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance);
                if (f != null)
                {
                    try { return f.GetValue(obj); } catch { }
                }
            }
            catch { }
            return null;
        }

        static double NumOf(object v)
        {
            if (v == null) return double.NaN;
            try
            {
                if (v is float f) return f;
                if (v is double d) return d;
                if (v is int i) return i;
                if (v is long l) return l;
                if (v is IConvertible c) return c.ToDouble(CultureInfo.InvariantCulture);
            }
            catch { }
            return double.NaN;
        }

        /// <summary>POST /send — locate GameObjects by name (contains match, including
        /// inactive) and BroadcastMessage a method into them. Lets us close popups /
        /// press UI buttons that need in-engine routing.</summary>
        public static string SendMessageJson(string goName, string method, string param, int maxTargets)
        {
            return OnMain(() =>
            {
                if (string.IsNullOrEmpty(goName) || string.IsNullOrEmpty(method))
                    return new Jw().StartObj().Prop("ok", false).Prop("error", "missing_go_or_method").EndObj().ToString();

                var sc = SceneManager.GetActiveScene();
                var roots = sc.GetRootGameObjects();
                var hits = new List<GameObject>();
                int budget = 20000;
                foreach (var r in roots)
                {
                    if (hits.Count >= Math.Max(1, maxTargets) || budget <= 0) break;
                    Search(r.transform, goName, Math.Max(1, maxTargets), ref budget, hits);
                }
                if (hits.Count == 0)
                    return new Jw().StartObj().Prop("ok", false).Prop("error", "go_not_found").Prop("q", goName).EndObj().ToString();

                var sent = new List<string>();
                var opts = SendMessageOptions.DontRequireReceiver;
                foreach (var go in hits)
                {
                    try
                    {
                        if (param == null) go.BroadcastMessage(method, opts);
                        else go.BroadcastMessage(method, param, opts);
                        sent.Add(PathOf(go.transform));
                    }
                    catch (Exception ex)
                    {
                        sent.Add("(err) " + PathOf(go.transform) + ": " + ex.Message);
                    }
                }

                var jw = new Jw().StartObj().Prop("ok", true).Prop("method", method).Prop("target", goName)
                    .Prop("sent", sent.Count).Name("targets").StartArr();
                foreach (var s in sent) jw.Str(trunc(s));
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

        public static string StaticsJson(string typeName, int max, int arrCap, int depth)
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
                // How deep to unroll sequences and how many elements to keep per
                // sequence. The old code was fixed at one level / 128 items, which
                // is why List<Il2CppStructArray<int>> came back as type names and
                // listMapDatas reported _count=250 but emitted 128.
                var ctx = new EmitCtx
                {
                    Depth = Math.Max(0, Math.Min(depth, 4)),
                    Cap = Math.Max(1, Math.Min(arrCap, 2000)),
                };

                // IL2CPP interop proxies surface native fields as static
                // properties with getters invoking the runtime; read those
                // first so values come from il2cpp, not the IntPtr plumbing.
                PropertyInfo[] props;
                try { props = type.GetProperties(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static); }
                catch { props = Array.Empty<PropertyInfo>(); }
                foreach (var p in props)
                {
                    if (written >= max) break;
                    var getter = p.GetGetMethod(true) ?? p.GetGetMethod(false);
                    if (getter == null || getter.IsAbstract) continue;
                    try
                    {
                        object v = getter.Invoke(null, null);
                        EmitAny(ref jw, p.Name, v, ref written, max, ctx);
                    }
                    catch { /* skip fields that interop refuses to read */ }
                }

                FieldInfo[] fields;
                try { fields = type.GetFields(BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static); }
                catch (Exception ex)
                {
                    if (written == 0)
                        return new Jw().StartObj().Prop("ok", false).Prop("error", "reflection_failed").Prop("detail", ex.Message).EndObj().ToString();
                    fields = Array.Empty<FieldInfo>();
                }

                foreach (var f in fields)
                {
                    if (written >= max) break;
                    if (f.Name.StartsWith("NativeFieldInfoPtr_", StringComparison.Ordinal) ||
                        f.Name.StartsWith("NativeMethodInfoPtr", StringComparison.Ordinal))
                        continue; // il2cpp plumbing pointers, not data
                    try
                    {
                        object v = f.GetValue(null);
                        EmitAny(ref jw, f.Name, v, ref written, max, ctx);
                    }
                    catch { /* skip fields that interop refuses to read */ }
                }

                jw.EndObj().Prop("written", written);
                if (ctx.Truncated) jw.Prop("truncated", true);
                jw.EndObj();
                return jw.ToString();
            }, 6000);
        }

        sealed class EmitCtx
        {
            public int Depth;                 // how many sequence levels to unroll
            public int Cap = 128;             // elements kept per sequence
            public int Budget = 80000;        // scalars total, so one huge field cannot
            public bool Truncated;            // blow the response or the logcat mirror
        }

        static void EmitAny(ref Jw jw, string name, object v, ref int written, int max, EmitCtx ctx)
        {
            if (written >= max) return;
            written++;

            if (v == null) { jw.Name(name).Null(); return; }

            int len;
            Func<int, object> get;
            if (ctx.Depth > 0 && TrySeq(v, out len, out get))
            {
                jw.Name(name);
                EmitSeq(ref jw, len, get, ctx.Depth, ctx);
                // Kept for compatibility: the full length, even when the array is
                // cut at Cap. `_count` is the number the old reports quoted.
                jw.Name(name + "_count").Num(len);
                return;
            }

            EmitScalar(ref jw, name, v);
        }

        static void EmitSeq(ref Jw jw, int len, Func<int, object> get, int depth, EmitCtx ctx)
        {
            int n = Math.Min(len, ctx.Cap);
            if (len > n) ctx.Truncated = true;
            jw.StartArr();
            for (int i = 0; i < n; i++)
            {
                if (ctx.Budget <= 0) { ctx.Truncated = true; break; }
                ctx.Budget--;
                object item = null;
                try { item = get(i); }
                catch { /* one unreadable element must not lose the whole array */ }

                int innerLen;
                Func<int, object> innerGet;
                if (depth > 1 && item != null && TrySeq(item, out innerLen, out innerGet))
                    EmitSeq(ref jw, innerLen, innerGet, depth - 1, ctx);
                else if (item == null) jw.Null();
                else EmitScalar(ref jw, null, item);
            }
            jw.EndArr();
        }

        static void EmitScalar(ref Jw jw, string name, object v)
        {
            var t = v.GetType();
            bool named = name != null;

            if (t == typeof(string)) { if (named) jw.Name(name); jw.Str(trunc((string)v)); return; }
            if (t == typeof(bool)) { if (named) jw.Name(name); jw.Bool((bool)v); return; }
            if (t == typeof(int) || t == typeof(long) || t == typeof(short) || t == typeof(byte) ||
                t == typeof(uint) || t == typeof(ulong) || t == typeof(ushort) ||
                t == typeof(sbyte) || t == typeof(float) || t == typeof(double) || t == typeof(decimal))
            {
                if (named) jw.Name(name);
                jw.Num(Convert.ToDouble(v, CultureInfo.InvariantCulture));
                return;
            }

            // A sequence we refused to unroll (depth exhausted) is reported with
            // its length, so the caller can ask for it with &depth= instead of
            // getting a bare type name that looks like missing data.
            int len;
            Func<int, object> get;
            if (TrySeq(v, out len, out get))
            {
                if (named) jw.Name(name);
                jw.Str("(" + t.Name + ",len=" + len + ")");
                return;
            }

            if (named) jw.Name(name);
            jw.Str("(" + t.Name + ")");
        }

        /// <summary>System arrays and il2cpp interop sequences are different animals:
        /// the interop ones are not System.Array and only expose Length/Count plus
        /// an Item indexer. Both are read the same way from here on.</summary>
        static bool TrySeq(object v, out int len, out Func<int, object> get)
        {
            len = 0;
            get = null;
            if (v == null) return false;

            if (v is Array a && a.Rank == 1)
            {
                len = a.Length;
                get = i => a.GetValue(i);
                return len > 0;
            }

            var t = v.GetType();
            bool sequence =
                t.Name == "Il2CppStructArray`1" || t.Name == "Il2CppReferenceArray`1" ||
                t.Name == "Il2CppStringArray" || t.Name == "List`1" ||
                (t.Namespace != null && t.Namespace.StartsWith("Il2Cpp", StringComparison.Ordinal));
            if (!sequence) return false;

            try
            {
                var lp = t.GetProperty("Length") ?? t.GetProperty("Count");
                var ix = t.GetProperty("Item");
                if (lp == null || ix == null) return false;
                len = Convert.ToInt32(lp.GetValue(v), CultureInfo.InvariantCulture);
                var target = v;
                get = i => ix.GetValue(target, new object[] { i });
                return len > 0;
            }
            catch { return false; }
        }

        static string trunc(string s) { return s != null && s.Length > 400 ? s.Substring(0, 400) : s; }

        static IEnumerable<Type> SafeTypes(Assembly asm)
        {
            Type[] tt = null;
            try { tt = asm.GetTypes(); }
            catch (ReflectionTypeLoadException ex) { tt = ex.Types; }
            catch { tt = null; }
            return tt ?? Array.Empty<Type>();
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
                    }
                    catch { }

                    foreach (var candidate in SafeTypes(asm))
                    {
                        if (candidate == null) continue;
                        if (candidate.Name == name)
                        {
                            if (candidate.FullName == name) return candidate;
                            // Prefer the game assembly when several types share a simple name.
                            if (asm.GetName().Name.IndexOf("Assembly-CSharp", StringComparison.OrdinalIgnoreCase) >= 0) return candidate;
                        }
                    }
                }

                foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
                {
                    foreach (var candidate in SafeTypes(asm))
                        if (candidate != null && candidate.Name == name) return candidate;
                }
            }
            catch { }
            return null;
        }

        /// <summary>Type-name discovery: dump the game's class names (by default
        /// matching a filter) so callers can find the exact names /statics wants.</summary>
        public static string TypesJson(string filter, int max)
        {
            var jw = new Jw().StartObj().Prop("ok", true).Prop("filter", filter).Prop("asmCount", AppDomain.CurrentDomain.GetAssemblies().Length).Name("matched").StartArr();
            int written = 0, total = 0;
            foreach (var asm in AppDomain.CurrentDomain.GetAssemblies())
            {
                if (asm.GetName().Name == "mscorlib" || asm.GetName().Name == "System") continue;
                foreach (var t in SafeTypes(asm))
                {
                    if (t == null) continue;
                    total++;
                    var fn = t.FullName ?? t.Name;
                    if (written < max && (filter.Length == 0 || fn.IndexOf(filter, StringComparison.OrdinalIgnoreCase) >= 0))
                    {
                        jw.StartObj().Prop("t", fn).Prop("asm", asm.GetName().Name).EndObj();
                        written++;
                    }
                }
            }
            jw.EndArr().Prop("typedTotal", total).Prop("written", written).EndObj();
            return jw.ToString();
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

        // â”€â”€ helpers

        /// <summary>Fetch a Unity property that may hit an unresolved icall on
        /// stripped IL2CPP builds; fall back instead of failing the probe.</summary>
        static object Safe(Func<object> f, object fallback)
        {
            try { return f(); } catch { return fallback; }
        }

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

    // â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ router

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
                        Copy(res, HttpResponse.Json(Bridge.StaticsJson(
                            req.Query.TryGetValue("type", out var t) ? t : "",
                            Q(req, "max", 200),
                            Q(req, "arr", 128),     // elements kept per array
                            Q(req, "depth", 2))));  // 2 = List<Array<int>> fully unrolled
                        return;

                    case "GET /anim":
                        Copy(res, HttpResponse.Json(Bridge.AnimJson(
                            req.Query.TryGetValue("name", out var an) ? an : "",
                            Q(req, "max", 50))));
                        return;

                    case "GET /types":
                        Copy(res, HttpResponse.Json(Bridge.TypesJson(req.Query.TryGetValue("filter", out var f) ? f : "", Q(req, "max", 500))));
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

                    case "POST /send":
                        Copy(res, HttpResponse.Json(Bridge.SendMessageJson(
                            req.Query.TryGetValue("go", out var gon) ? gon : "",
                            req.Query.TryGetValue("m", out var mm) ? mm : "",
                            req.Query.TryGetValue("p", out var pp) ? pp : null,
                            Q(req, "targets", 5))));
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
