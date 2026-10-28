// BepInEx 5 (Mono) adapter — for Mono builds / desktop test runs of the probe.
// Build with: dotnet build -p:Loader=BepInEx5 -p:UnityManagedDir=<game>/Managed
using BepInEx;
using Ramus.Bridge;

namespace Ramus.Bridge.Adapters
{
    [BepInPlugin(Guid, "Ramus Runtime Bridge", Version)]
    public sealed class BepInEx5Plugin : BaseUnityPlugin
    {
        public const string Guid = "dev.ramus.bridge";
        public const string Version = "1.0.0";

        private void Awake()
        {
            Bridge.Init(msg => Logger.LogInfo(msg));
            BridgeHost.Create();
            Logger.LogInfo("Ramus bridge ready on port " + Bridge.Config.Port);
        }

        private void OnDestroy()
        {
            Bridge.Shutdown();
        }
    }
}
