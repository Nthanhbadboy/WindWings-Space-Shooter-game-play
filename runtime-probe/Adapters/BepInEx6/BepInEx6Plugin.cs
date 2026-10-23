// BepInEx 6 (IL2CPP) adapter — BepInEx.Unity.IL2CPP.BasePlugin.
// Build with: dotnet build -p:Loader=BepInEx6 -p:BepInExRoot=<game>/BepInEx
using System;
using System.Linq;
using System.Reflection;
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
            TryInjectBridgeHost();
            Bridge.Init(msg => Log.LogInfo(msg));
            BridgeHost.Create();
            Log.LogInfo("Ramus bridge ready on port " + Bridge.Config.Port);
        }

        // Il2CppInterop ClassInjector signatures vary across forks/versions
        // (RegisterTypeInIl2Cpp / RegisterDerivedType, generic or Type-based,
        // with and without options params). Resolve whichever exists via
        // reflection; registration failure must never kill the chainload.
        private void TryInjectBridgeHost()
        {
            try
            {
                var injector = AppDomain.CurrentDomain.GetAssemblies()
                    .Select(a => a.GetType("Il2CppInterop.Runtime.Injection.ClassInjector"))
                    .FirstOrDefault(t => t != null);
                if (injector == null)
                {
                    Log.LogInfo("Il2CppInterop ClassInjector type not found; skipping registration");
                    return;
                }
                var cands = injector.GetMethods(BindingFlags.Public | BindingFlags.Static)
                    .Where(m => m.Name == "RegisterTypeInIl2Cpp" || m.Name == "RegisterDerivedType")
                    .OrderBy(m => m.GetParameters().Length).ToList();
                foreach (var raw in cands)
                {
                    var m = raw;
                    if (m.IsGenericMethodDefinition)
                    {
                        if (m.GetGenericArguments().Length != 1) continue;
                        m = m.MakeGenericMethod(typeof(BridgeHost));
                    }
                    var pars = m.GetParameters();
                    var args = new object[pars.Length];
                    var ok = true;
                    for (int i = 0; i < pars.Length; i++)
                    {
                        if (pars[i].HasDefaultValue) args[i] = pars[i].DefaultValue;
                        else
                        {
                            try { args[i] = Activator.CreateInstance(pars[i].ParameterType); }
                            catch { ok = false; break; }
                        }
                    }
                    if (!ok) continue;
                    try
                    {
                        m.Invoke(null, args);
                        Log.LogInfo("BridgeHost registered via " + injector.FullName + "." + raw.Name);
                        return;
                    }
                    catch (Exception ex)
                    {
                        Log.LogWarning("injector overload " + raw.Name + "/" + pars.Length +
                                       " failed: " + (ex.InnerException ?? ex).Message);
                    }
                }
                Log.LogWarning("no ClassInjector overload worked for BridgeHost");
            }
            catch (Exception ex)
            {
                Log.LogWarning("BridgeHost registration skipped: " + ex.Message);
            }
        }
    }
}
