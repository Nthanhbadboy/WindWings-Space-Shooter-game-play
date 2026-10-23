// MelonLoader / LemonLoader adapter.
// Build with: dotnet build -p:Loader=MelonLoader -p:MelonDir=<MelonLoader folder>
using MelonLoader;
using Ramus.Bridge;

[assembly: MelonInfo(typeof(Ramus.Bridge.Adapters.MelonBridge), "Ramus Runtime Bridge", "1.0.0", "Ramus")]
[assembly: MelonGame(null, null)]

namespace Ramus.Bridge.Adapters
{
    public sealed class MelonBridge : MelonMod
    {
        public override void OnInitializeMelon()
        {
            Bridge.Init(msg => LoggerInstance.Msg(msg));
        }

        public override void OnApplicationStart()
        {
            // Unity is alive from here on, so the host GameObject can be created.
            BridgeHost.Create();
            LoggerInstance.Msg("Ramus bridge ready on port " + Bridge.Config.Port);
        }

        public override void OnApplicationQuit()
        {
            Bridge.Shutdown();
        }
    }
}
