// BepInEx 6 (IL2CPP) adapter — BepInEx.Unity.IL2CPP.BasePlugin.
// Build with: dotnet build -p:Loader=BepInEx6 -p:BepInExRoot=<game>/BepInEx
using BepInEx;
using BepInEx.Unity.IL2CPP;
using Ramus.Bridge;

namespace Ramus.Bridge.Adapters
{
    [BepInPlugin(Guid, "Ramus Runtime Bridge", Version)]
    public sealed class BepInEx6Plugin : BasePlugin
    {
        public const string Guid = "dev.ramus.bridge";
        public const string Version = "1.0.0";

        public override void Load()
        {
            Bridge.Init(msg => Log.LogInfo(msg));
            BridgeHost.Create();
            Log.LogInfo("Ramus bridge ready on port " + Bridge.Config.Port);
        }
    }
}
