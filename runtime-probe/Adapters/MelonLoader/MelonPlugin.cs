// MelonLoader / LemonLoader adapter.
//
// Version note (verified against LavaGang/MelonLoader v0.7.3 source):
//   MelonBase no longer declares OnApplicationStart — it was removed after 0.6.x.
//   OnInitializeMelon / OnUpdate / OnApplicationQuit exist in BOTH 0.6 and 0.7,
//   so those are the only hooks this adapter touches. The host GameObject is
//   created lazily from OnUpdate, which is the first guaranteed "Unity is alive"
//   callback in either version.
//
// Build: dotnet build -p:Loader=MelonLoader -p:MelonDir=<MelonLoader folder>
using MelonLoader;
using Ramus.Bridge;

[assembly: MelonInfo(typeof(Ramus.Bridge.Adapters.MelonBridge), "Ramus Runtime Bridge", "1.0.0", "Ramus")]
[assembly: MelonGame(null, null)]

namespace Ramus.Bridge.Adapters
{
    public sealed class MelonBridge : MelonMod
    {
        private bool _hostCreated;

        public override void OnInitializeMelon()
        {
            // Pure .NET work only: the TCP listener does not touch the Unity API.
            Bridge.Init(msg => LoggerInstance.Msg(msg));
        }

        public override void OnUpdate()
        {
            if (_hostCreated) return;
            _hostCreated = true;

            // First OnUpdate means Unity is running, so a GameObject can be made.
            BridgeHost.Create();
            LoggerInstance.Msg("Ramus bridge ready on port " + Bridge.Config.Port);
        }

        public override void OnApplicationQuit()
        {
            Bridge.Shutdown();
        }
    }
}
