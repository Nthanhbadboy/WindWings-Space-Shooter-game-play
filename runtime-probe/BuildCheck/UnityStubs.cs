// Minimal Unity API surface used by RamusBridge.cs — compile-time check only.
//
// This file is NEVER shipped. Its only job is to let CI prove that
// RamusBridge.cs type-checks without a Unity install:
//
//   dotnet build runtime-probe/RamusBridge.csproj -p:Loader=Core -p:StubUnity=true
//
// Signatures mirror UnityEngine 2022.3 (CoreModule / ImageConversionModule /
// ScreenCaptureModule). If the bridge starts using a new Unity API, add it here
// and the stub build will tell you whether the call is shaped correctly.

using System;

namespace UnityEngine
{
    public enum HideFlags { None = 0, HideInHierarchy = 1, HideAndDontSave = 61 }
    public enum LogType { Error = 0, Assert = 1, Warning = 2, Log = 3, Exception = 4 }
    public enum RuntimePlatform { Android = 11, WindowsPlayer = 2, LinuxPlayer = 7 }

    public struct Vector3
    {
        public float x, y, z;
        public Vector3(float x, float y, float z) { this.x = x; this.y = y; this.z = z; }
        public static Vector3 zero => new Vector3(0, 0, 0);
    }

    public static class Mathf
    {
        public static float Max(float a, float b) => a > b ? a : b;
        public static int Max(int a, int b) => a > b ? a : b;
    }

    public class Object
    {
        public string name { get; set; }
        public HideFlags hideFlags { get; set; }
        public static void DontDestroyOnLoad(Object target) { }
        public static void Destroy(Object obj) { }
        public static implicit operator bool(Object exists) => !ReferenceEquals(exists, null);
    }

    public class Component : Object
    {
        // Setter exists so the stub GameObject can wire itself up; real Unity is
        // get-only, and RamusBridge.cs never assigns these, which the other
        // targets prove.
        public GameObject gameObject { get; set; }
        public Transform transform { get; }
    }

    public class Behaviour : Component
    {
        public bool enabled { get; set; }
    }

    public class MonoBehaviour : Behaviour { }

    public class Transform : Component
    {
        public Vector3 position { get; set; }
        public Vector3 localPosition { get; set; }
        public Transform parent { get; set; }
        public int childCount { get; }
        public Transform GetChild(int index) => null;
    }

    public class GameObject : Object
    {
        readonly System.Collections.Generic.List<Component> _components = new System.Collections.Generic.List<Component>();
        readonly Transform _transform;

        public GameObject() : this(null) { }
        public GameObject(string name)
        {
            if (name != null) this.name = name;
            _transform = new Transform { gameObject = this };
            _components.Add(_transform);
        }

        public Transform transform => _transform;
        public bool activeSelf { get; }
        public bool activeInHierarchy { get; }
        public string tag { get; set; }
        public int layer { get; set; }
        public T AddComponent<T>() where T : Component
        {
            var c = (T)Activator.CreateInstance(typeof(T));
            c.gameObject = this;
            _components.Add(c);
            return c;
        }

        public T[] GetComponents<T>()
        {
            var out_ = new System.Collections.Generic.List<T>();
            foreach (var c in _components) if (c is T t) out_.Add(t);
            return out_.ToArray();
        }

        public Component[] GetComponents(Type type)
        {
            var out_ = new System.Collections.Generic.List<Component>();
            foreach (var c in _components) if (type.IsInstanceOfType(c)) out_.Add(c);
            return out_.ToArray();
        }

        // Message routing. The phone build references the real UnityEngine and
        // these exist there; the stubs exist so `core` and the self-test can
        // compile the same file, so they have to declare the same surface.
        public void SendMessage(string methodName) { }
        public void SendMessage(string methodName, object value) { }
        public void SendMessage(string methodName, SendMessageOptions options) { }
        public void SendMessage(string methodName, object value, SendMessageOptions options) { }
        public void BroadcastMessage(string methodName) { }
        public void BroadcastMessage(string methodName, object value) { }
        public void BroadcastMessage(string methodName, SendMessageOptions options) { }
        public void BroadcastMessage(string methodName, object value, SendMessageOptions options) { }
    }

    public enum SendMessageOptions
    {
        RequireReceiver = 0,
        DontRequireReceiver = 1,
    }

    public class Texture : Object { }

    public class Texture2D : Texture
    {
        public int width { get; }
        public int height { get; }
    }

    public static class ScreenCapture
    {
        public static Texture2D CaptureScreenshotAsTexture() => null;
    }

    public static class ImageConversion
    {
        public static byte[] EncodeToPNG(this Texture2D tex) => null;
    }

    public static class Debug
    {
        public static void Log(object message) { }
        public static void LogWarning(object message) { }
        public static void LogError(object message) { }
    }

    public static class Time
    {
        public static float unscaledDeltaTime { get; }
        public static float realtimeSinceStartup { get; }
        public static float timeScale { get; set; }
        public static int frameCount { get; }
    }

    public static class Screen
    {
        public static int width { get; }
        public static int height { get; }
        public static float dpi { get; }
        public static bool fullScreen { get; }
    }

    public static class QualitySettings
    {
        // Unity returns an empty array, never null. A null here made the
        // self-test report a phantom 500 on /state.
        public static string[] names { get; } = new string[0];
        public static int GetQualityLevel() => 0;
        public static int vSyncCount { get; set; }
    }

    public static class SystemInfo
    {
        public static string deviceModel { get; }
        public static string operatingSystem { get; }
        public static int processorCount { get; }
        public static int systemMemorySize { get; }
        public static string graphicsDeviceName { get; }
    }

    public static class Application
    {
        public delegate void LogCallback(string condition, string stackTrace, LogType type);
        public static event LogCallback logMessageReceivedThreaded;
        public static string unityVersion { get; }
        public static RuntimePlatform platform { get; }
        public static bool isPlaying { get; }
        public static int targetFrameRate { get; set; }
        public static void Quit() { }
    }
}

namespace UnityEngine.SceneManagement
{
    public struct Scene
    {
        public string name { get; }
        public string path { get; }
        public int buildIndex { get; }
        public bool isLoaded { get; }
        public GameObject[] GetRootGameObjects() => new GameObject[0];
    }

    public static class SceneManager
    {
        public static Scene GetActiveScene() => default;
        public static int sceneCount { get; }
    }
}
