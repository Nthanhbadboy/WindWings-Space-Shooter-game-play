// Headless self-test for the embedded bridge HTTP server.
//
// Boots the real RamusBridge.cs against the compile-time UnityEngine stub, then
// drives every endpoint over a real TCP socket with HttpClient. The bridge's
// handlers marshal through OnMain/Func, so this also exercises the main-thread
// queue: the tick loop below stands in for MonoBehaviour.Update.
//
// Exit code 0 = everything passed, 1 = at least one check failed.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net.Http;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Ramus.Bridge;

static class Program
{
    const int Port = 18080;
    static int _passed;
    static readonly List<string> Failed = new List<string>();

    static void Check(string name, bool ok, string detail = "")
    {
        if (ok) { _passed++; Console.WriteLine("  PASS  " + name); return; }
        Failed.Add(name + (string.IsNullOrEmpty(detail) ? "" : " — " + detail));
        Console.WriteLine("  FAIL  " + name + (string.IsNullOrEmpty(detail) ? "" : " — " + detail));
    }

    static async Task<int> Main()
    {
        Environment.SetEnvironmentVariable("RAMUS_BRIDGE_PORT", Port.ToString());
        Environment.SetEnvironmentVariable("RAMUS_BRIDGE_BIND", "127.0.0.1");
        Environment.SetEnvironmentVariable("RAMUS_BRIDGE_TOKEN", "");
        Environment.SetEnvironmentVariable("RAMUS_BRIDGE_MIRROR", "0");

        Console.WriteLine("== boot");
        Bridge.Init(m => Console.WriteLine("  [log] " + m));

        if (!Bridge.Running)
        {
            Console.WriteLine("FATAL: the HTTP server did not start listening");
            return 1;
        }
        Check("server started", Bridge.Running);
        Check("config picked up the env port", Bridge.Config.Port == Port, "port=" + Bridge.Config.Port);

        // Stand-in for Update(): drain the queue that HTTP threads post into.
        var stop = new CancellationTokenSource();
        var ticker = Task.Run(async () =>
        {
            while (!stop.IsCancellationRequested)
            {
                try { Bridge.Tick(); } catch (Exception ex) { Console.WriteLine("  [tick] " + ex.Message); }
                await Task.Delay(5).ConfigureAwait(false);
            }
        });

        using (var http = new HttpClient
        {
            BaseAddress = new Uri("http://127.0.0.1:" + Port),
            Timeout = TimeSpan.FromSeconds(15),
        })
        {
            // ── GET endpoints: every one must answer with valid JSON ──────────
            var gets = new[]
            {
                "/health",
                "/state",
                "/scene?max=5",
                "/hierarchy?depth=1&max=20",
                "/find?name=Player&max=5",
                "/statics?type=Player_Get_Datas&max=5",
                "/logs?n=10",
                "/metrics",
            };

            foreach (var path in gets)
            {
                var sw = Stopwatch.StartNew();
                try
                {
                    using var res = await http.GetAsync(path).ConfigureAwait(false);
                    string body = await res.Content.ReadAsStringAsync().ConfigureAwait(false);
                    sw.Stop();

                    // Include the body on failure: a 500 from this server carries
                    // the exception type, which is the difference between "our bug"
                    // and "the stub returned null where Unity returns an empty array".
                    Check("GET " + path + " → 200", (int)res.StatusCode == 200,
                          "status=" + (int)res.StatusCode + " body=" + First(body, 200));
                    Check("GET " + path + " → JSON", IsJson(body), First(body, 120));
                    Check("GET " + path + " → fast", sw.ElapsedMilliseconds < 8000, sw.ElapsedMilliseconds + " ms");
                }
                catch (Exception ex)
                {
                    Check("GET " + path, false, ex.GetType().Name + ": " + ex.Message);
                }
            }

            // /health is the endpoint CI depends on, so assert its shape.
            try
            {
                using var res = await http.GetAsync("/health").ConfigureAwait(false);
                string body = await res.Content.ReadAsStringAsync().ConfigureAwait(false);
                using var doc = JsonDocument.Parse(body);
                var root = doc.RootElement;
                Check("/health has ok=true",
                      root.TryGetProperty("ok", out var ok) && ok.ValueKind == JsonValueKind.True, body);
                Check("/health has scene", root.TryGetProperty("scene", out _), body);
                Check("/health has unity", root.TryGetProperty("unity", out _), body);
                Check("/health content-type is JSON",
                      res.Content.Headers.ContentType != null &&
                      res.Content.Headers.ContentType.MediaType.Contains("json"),
                      res.Content.Headers.ContentType?.MediaType);
            }
            catch (Exception ex)
            {
                Check("/health shape", false, ex.Message);
            }

            // ── screenshot: the stub returns null, so 503 is the honest answer ─
            try
            {
                using var res = await http.GetAsync("/screenshot").ConfigureAwait(false);
                int code = (int)res.StatusCode;
                // 503 = capture failed (stub), 403 = disabled by config. Both prove routing.
                Check("/screenshot routed (503 or 403)", code == 503 || code == 403, "status=" + code);
            }
            catch (Exception ex)
            {
                Check("/screenshot", false, ex.Message);
            }

            // ── unknown route must be a clean 404, not a dropped connection ────
            try
            {
                using var res = await http.GetAsync("/definitely-not-a-route").ConfigureAwait(false);
                Check("GET unknown → 404", (int)res.StatusCode == 404, "status=" + (int)res.StatusCode);
            }
            catch (Exception ex)
            {
                Check("GET unknown → 404", false, ex.Message);
            }

            // ── POST /timescale round-trips a query parameter ─────────────────
            try
            {
                using var res = await http.PostAsync("/timescale?v=1", null).ConfigureAwait(false);
                string body = await res.Content.ReadAsStringAsync().ConfigureAwait(false);
                Check("POST /timescale → 200", (int)res.StatusCode == 200, "status=" + (int)res.StatusCode);
                Check("POST /timescale → ok", body.Contains("\"ok\":true"), First(body, 160));
            }
            catch (Exception ex)
            {
                Check("POST /timescale", false, ex.Message);
            }

            // ── 20 concurrent requests: the queue and the socket must hold up ──
            var tasks = new List<Task<bool>>();
            for (int i = 0; i < 20; i++)
            {
                tasks.Add(Task.Run(async () =>
                {
                    using var res = await http.GetAsync("/health").ConfigureAwait(false);
                    return (int)res.StatusCode == 200;
                }));
            }
            bool[] results = await Task.WhenAll(tasks).ConfigureAwait(false);
            int okCount = 0;
            foreach (var r in results) if (r) okCount++;
            Check("20 concurrent /health → all 200", okCount == 20, okCount + "/20");
        }

        // ── shutdown must release the port ───────────────────────────────────
        Bridge.Shutdown();
        Check("server stopped", !Bridge.Running);

        bool portFree;
        try
        {
            var l = new System.Net.Sockets.TcpListener(System.Net.IPAddress.Loopback, Port);
            l.Start();
            l.Stop();
            portFree = true;
        }
        catch { portFree = false; }
        Check("port released after shutdown", portFree);

        stop.Cancel();
        try { await ticker.ConfigureAwait(false); } catch { /* ignore */ }

        Console.WriteLine();
        Console.WriteLine("=== selftest: " + _passed + " passed, " + Failed.Count + " failed");
        foreach (var f in Failed) Console.WriteLine("    ✗ " + f);
        return Failed.Count == 0 ? 0 : 1;
    }

    static bool IsJson(string s)
    {
        if (string.IsNullOrWhiteSpace(s)) return false;
        try { using var d = JsonDocument.Parse(s); return true; }
        catch { return false; }
    }

    static string First(string s, int n) => s == null ? "<null>" : (s.Length <= n ? s : s.Substring(0, n) + "…");
}
