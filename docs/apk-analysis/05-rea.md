# Reverse Engineering Report: com.Wind.wings.Space.Shooter.apk

_ZIP container | 118,135,473 bytes (112.6 MiB) | SHA-256 HEX_REDACTED_

## Executive Summary

Observed: com.Wind.wings.Space.Shooter.apk is ZIP container (118,135,473 bytes (112.6 MiB)); native code analysis does not apply.

- Inferred: the file is not packed (packing score 2).
- Observed: 27 indicators extracted, including 1 URL.

Evidence labels: Observed facts are read directly from the file; Derived facts are computed deterministically from observed data; Inferred statements are interpretations that an analyst should confirm.

## Identity and Fingerprints

| Property | Value |
| --- | --- |
| File name | com.Wind.wings.Space.Shooter.apk |
| Size | 118,135,473 bytes (112.6 MiB) |
| Format | ZIP container |
| Entropy (bits/byte) | 7.21 |
| MD5 | e897cbe6c78021086157c39336e5a2af |
| SHA-1 | HEX_REDACTED |
| SHA-256 | HEX_REDACTED |

## Strings and Indicators

Observed: 50,331 printable strings (50000 ASCII, 331 UTF-16LE).

### Indicators

| Type | Value | File offset |
| --- | --- | --- |
| Windows path | ^DF:\o; | 0xf7eb |
| Windows path | \\Rt* | 0x6af5b |
| Windows path | tR:\GWn | 0x6e0a2 |
| Windows path | X[n:\ | 0x6e7e2 |
| Windows path | %\?st | 0xef863 |
| Email address | k@@.BR | 0x1890a2 |
| Windows path | \\[y? | 0x19b669 |
| Windows path | %\Nc(8 | 0x33d6c6 |
| Windows path | %\O0~ | 0x356dc7 |
| Windows path | %\AK( | 0x41dd4a |
| Windows path | KWo:\ | 0x430627 |
| Windows path | \\(69 | 0x447d01 |
| Windows path | \\'RN | 0x5d63bf |
| Windows path | 	xB:\ | 0x98aae2 |
| Windows path | %\\*3 | 0x9bf353 |
| Windows path |  I.b:\ | 0xc240b4 |
| URL | http://chilliant.blogspot.com.au/2012/08/srgb-aG | 0xce335b |
| Windows path | \\ZVQg | 0xd14826 |
| Windows path | \\\Aj | 0xd1e1d6 |
| Windows path | \\\Rh~S\| | 0xd400d9 |
| Windows path | Ve:\P@G | 0xd4227a |
| Windows path | \\ aa | 0xd4d348 |
| Windows path | \\A.6F\\ | 0xd786c9 |
| Email address | i@...Aj | 0xd8ee8f |
| Windows path | \\\Mk | 0xd9769d |
| Windows path | \\hhh | 0xdab751 |
| Windows path | \\\\C1 | 0xdb55ff |

### String Sample

````text
0000001e  AndroidManifest.xml
00003009  DebugProbesKt.bin
00003344  META-INF/androidx.activity_activity-ktx.version
00003398  META-INF/androidx.activity_activity.version
000033e8  META-INF/androidx.annotation_annotation-experimental.version1.4.1
00003448  META-INF/androidx.appcompat_appcompat-resources.version
000034a4  META-INF/androidx.appcompat_appcompat.version
000035e8  META-INF/androidx.browser_browser.version
00003638  META-INF/androidx.cardview_cardview.version
00003688  META-INF/androidx.coordinatorlayout_coordinatorlayout.version
000036ec  META-INF/androidx.core_core-ktx.version
00003739  META-INF/androidx.core_core.version1.13.1
00003781  META-INF/androidx.credentials_credentials-play-services-auth.version
000037f1  META-INF/androidx.credentials_credentials.version
0000384d  META-INF/androidx.cursoradapter_cursoradapter.version
000038a8  META-INF/androidx.customview_customview.version
000038fc  META-INF/androidx.datastore_datastore-core.version
00003954  META-INF/androidx.datastore_datastore-preferences.version
000039b4  META-INF/androidx.datastore_datastore.version
00003a08  META-INF/androidx.documentfile_documentfile.version
00003a60  META-INF/androidx.drawerlayout_drawerlayout.version
00003ab8  META-INF/androidx.exifinterface_exifinterface.version
00003b14  META-INF/androidx.fragment_fragment.version
00003b64  META-INF/androidx.interpolator_interpolator.version
00003bbc  META-INF/androidx.legacy_legacy-support-core-ui.version
00003c18  META-INF/androidx.legacy_legacy-support-core-utils.version
00003c78  META-INF/androidx.legacy_legacy-support-v4.version
0000421f  META-INF/androidx.loader_loader.version
0000426c  META-INF/androidx.localbroadcastmanager_localbroadcastmanager.version
000042d8  META-INF/androidx.media_media.version
00004324  META-INF/androidx.print_print.version
00004370  META-INF/androidx.privacysandbox.ads_ads-adservices-java.version1.1.0-beta11
000043db  META-INF/androidx.privacysandbox.ads_ads-adservices.version
00004418  1.1.0-beta11
00004443  META-INF/androidx.profileinstaller_profileinstaller.version
000044fc  META-INF/androidx.room_room-runtime.version
0000454c  META-INF/androidx.savedstate_savedstate-ktx.version
000045a4  META-INF/androidx.savedstate_savedstate.version
000045f8  META-INF/androidx.slidingpanelayout_slidingpanelayout.version
0000465c  META-INF/androidx.sqlite_sqlite-framework.version
000046b4  META-INF/androidx.sqlite_sqlite.version
00004700  META-INF/androidx.startup_startup-runtime.version
00004758  META-INF/androidx.swiperefreshlayout_swiperefreshlayout.version
000047bc  META-INF/androidx.tracing_tracing.version
0000480c  META-INF/androidx.vectordrawable_vectordrawable-animated.version1.1.0
00004870  META-INF/androidx.vectordrawable_vectordrawable.version
000048cc  META-INF/androidx.versionedparcelable_versionedparcelable.version
00004934  META-INF/androidx.viewpager_viewpager.version
00004988  META-INF/androidx.webkit_webkit.version
000049d5  META-INF/androidx.work_work-runtime-ktx.version2.7.0
00004a28  META-INF/androidx.work_work-runtime.version
00004b03  META-INF/com/applovin/mediation/bytedance-adapter/verification.properties
00004bf2  META-INF/com/applovin/mediation/fyber-adapter/verification.properties
00004cdb  META-INF/com/applovin/mediation/google-ad-manager-adapter/verification.properties
00004dd7  META-INF/com/applovin/mediation/google-adapter/verification.properties
00004ec0  META-INF/com/applovin/mediation/inmobi-adapter/verification.properties
00004fa9  META-INF/com/applovin/mediation/ironsource-adapter/verification.properties
00005097  META-INF/com/applovin/mediation/mintegral-adapter/verification.properties
00005185  META-INF/com/applovin/mediation/unityads-adapter/verification.properties
00005272  META-INF/com/applovin/mediation/vungle-adapter/verification.properties
000059ac   .BAq\0r8
0000815e  META-INF/com/pangle/global/pag-sdk/verification.propertiesS
0000840e  META-INF/com.android.games.engine.build_fingerprint
000084a6  META-INF/kotlinx_coroutines_android.version
000084f8  META-INF/kotlinx_coroutines_core.version1.10.2PK
00008544  META-INF/kotlinx_coroutines_play_services.version
0000859c  META-INF/services/kb.m0
000085d8  META-INF/services/pb.u
00008614  androidsupportmultidexversion.txt
00008b94  assets/ad-viewer/omid-session-client-v1.js
0000bffc  \=}MO#	G
0000f8af  assets/audience_network.dex,
00012a4a  ,AP 3e	c
000554dd  p]AFQU}b
0007a69a  /a}lIf9'
000820af  qwEg\[os[
000bd065  3wk	u0#V
000bebe6  eV:9os31
000e0c41  "I$HR\}$9qo
000e1d06  euu]]]pA]
000f5868  }0Z_lza]
00127f5b  Ceqyiyueq
0012849b  cAM}EEU]EAY
0012af4f  Wieuma]]
0012cac5  }HiLNJ]JAJ
00135b5d  1g$}HJII
0015f82e  RI[seB7{
0016b9b5  6pYIUQEi#
001796c6  qA	 RT,_
0018ec01  }mVE444L
001b925e  I.zjHE3:
001bad2f  NA/TOLU	t]
001bf591  J	2ALGAk4p
001c26f2  assets/bin/Data/Managed/Metadata/global-metadata.datT
0020d56a  lNU17$[t
00217d6b  60-iyO	e
00221fb5  Oa%uphWO
002220f7  TV{zxIA?T
002322c4  uHYvOG#K
00239b44  ZgobsRIEz
0029fb01  EYiQVN:w
002a3bb9  IF=ECmEZ
00337572   MMjo-jomjo
00355676  :ijP]5IS
00368801  i\#h\#i\
003bc413  50SZ\ooi
003fe8b2  [[v/.Do_
00403a92  I?_M?_K?
0040483a  I?_M?_K?
004061d1  N?_N?_I?
0040670f  O?/H?/L?/I?
0040721e  lL?/I?/M?/K?/O?
00407317  I??M??K?
004073e0  lL?/I?/M?/K?/O?
0040750c  lL?/I?/K?
0040b36a  E?{E?{G?
00415cc8  V[EO17oE?
0041f6ad  assets/bin/Data/Managed/Resources/mscorlib.dll-resources.dat
004281e6  z83J-Vii$
0043c5c0  PW[I[mEzf
0043e383  assets/bin/Data/RuntimeInitializeOnLoads.json
0043e7e3  assets/bin/Data/ScriptingAssemblies.json
0043eb96  assets/bin/Data/boot.config5
0043ec4f  assets/bin/Data/data.unity3d
00440e11  globalgamemanagers
00440e2e  Resources/unity_builtin_extra
00441213  globalgamemanagers.assets#
00441234  Library/unity default resourcesd
00441268  _builtin_extraY
00441279  bsharedU
004412a9  qGCenter
0044134e  ublic.app-category.
004413df  Very Low
00441423  Horizontal
00441536  joystick button 0
00441577  oreturn\
004415cc  Device _
004415d6  /touchpad h
004417f0  bMiddlel
00441995  Combinedw
004419c6  al pad. These values are repli
00441a23  FxTemporaire  
00441a4a  Ignore Raycastx
00441a87  BlackHole
00441abb  nalErrorShader,
00441ae2  -ColoredL
00441b01  GUI/Text 
00441b18  FrameDebu
00441b3a  cLegacyV
00441b56  sBumped 3
````

## Packing and Obfuscation

Inferred: the target is not packed (score 2; threshold 3).

- Whole-file entropy is 7.21 bits/byte, typical of packed data (weight 2)

## Methodology and Limitations

- Identified the format from file signatures and fingerprinted the file with MD5, SHA-1, and SHA-256.
- Parsed PE, ELF, and Mach-O headers, sections, imports, exports, symbols, and build metadata.
- Measured Shannon entropy for the file and every section.
- Extracted ASCII and UTF-16LE strings and classified network, path, registry, and command indicators.
- Classified imported APIs into capability categories and evaluated security mitigations from header fields.
- Disassembled x86/x86-64 with iced-x86 and every other supported architecture through an embedded SLEIGH engine, by recursive descent.
- Ranked functions by the capabilities and indicators they touch and listed the most relevant ones.

### Limitations

- Analysis is static: the target is never executed, so run-time behavior is inferred, not observed.
- Imports show what a program can call, not what it does; dynamically resolved APIs are invisible to import analysis.
- Disassembly covers code reachable from the entry point, exports, and symbols; indirect-only code may be missed.
- A few architectures are parsed but not yet disassembled; for those, code analysis is omitted.

## Detected Capabilities

Derived: capabilities matched from the embedded rule pack against imports, strings, and recovered instructions.

| Capability | Namespace | Scope | ATT&CK / MBC |
| --- | --- | --- | --- |
| detect virtual machine | anti-analysis/anti-vm/vm-detection | file | Defense Evasion::Virtualization/Sandbox Evasion [T1497]; Anti-Behavioral Analysis::Virtual Machine Detection [B0009] |
| base64 alphabet | data-manipulation/encoding/base64 | file | Data::Encode Data::Base64 [C0026.001] |
| MZ header | executable/pe | file | none |
| managed .NET assembly | runtime/dotnet | file | none |
| MSVC toolchain | compiler/msvc | file | none |
| zlib library | lib/zlib | file | none |

## Cryptographic Constants

Derived: cryptographic constants identified by table signature in the target.

| Address | Constant | Kind |
| --- | --- | --- |
| 0x4b18070 | TEA/XTEA delta | block-cipher |
| 0x6a96eda | TEA/XTEA delta | block-cipher |
| 0x6da3d78 | TEA/XTEA delta | block-cipher |
| 0x5ae6174 | ChaCha sigma | stream-cipher |
| 0x5c09a08 | ChaCha sigma | stream-cipher |
| 0x4cd81df | base64 alphabet | encoding |
| 0x5d69cc0 | base64 alphabet | encoding |
| 0x6258d7c | base64 alphabet | encoding |
| 0x64b8b20 | base64 alphabet | encoding |
| 0x6591ce8 | base64 alphabet | encoding |
| 0x65a3c8d | base64 alphabet | encoding |
| 0x6c136a5 | base64 alphabet | encoding |

## Go Binary

Go binary (): package , 0 dependencies.

## Coverage & Limitations

Coverage: com.Wind.wings.Space.Shooter.apk parsed as ZIP container; 0 functions and 0 instructions recovered across 50331 strings. Limitations: 16351232 bytes of high-entropy (encrypted or compressed) regions were not decrypted; no executable header was parsed, so imports and mitigations are unavailable. An audit-grade evidence bundle (`re-<name>.evidence.json`) lists every finding with a stable content-addressed ID and can be checked offline with `rea verify`.

rea: reverse engineering /tmp/apk/parts/com.Wind.wings.Space.Shooter.apk
/tmp/apk/parts/re-com.Wind.wings.Space.Shooter.md
/tmp/apk/parts/re-com.Wind.wings.Space.Shooter.pdf
