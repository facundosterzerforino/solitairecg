#!/usr/bin/env python
"""Offline build of SolitaireCG 3.4.1 (xt550-libre) for Android 2.3.

Only explicit local inputs: JDK, Android build-tools (aapt, D8, zipalign,
apksigner) and a platform android.jar used at compile time only.
"""
import argparse, hashlib, os, pathlib, shutil, subprocess, zipfile


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for a in ('--jdk', '--build-tools', '--android-jar', '--keystore', '--storepass-file'):
        p.add_argument(a, required=True)
    p.add_argument('--alias', default='music')
    a = p.parse_args()
    repo = pathlib.Path(__file__).resolve().parent
    root = repo / 'app' / 'src' / 'main'
    for secret in (a.keystore, a.storepass_file):
        if pathlib.Path(secret).resolve().is_relative_to(repo):
            raise SystemExit('Signing files must be outside the source tree')
    sfx = '.exe' if os.name == 'nt' else ''
    jdk, bt = pathlib.Path(a.jdk), pathlib.Path(a.build_tools)
    java, javac = jdk / 'bin' / ('java' + sfx), jdk / 'bin' / ('javac' + sfx)
    aapt, align = bt / ('aapt' + sfx), bt / ('zipalign' + sfx)
    d8, signer = bt / 'lib' / 'd8.jar', bt / 'lib' / 'apksigner.jar'
    out = repo / 'build'
    if out.exists(): shutil.rmtree(out)
    for d in ('gen', 'classes', 'dex'): (out / d).mkdir(parents=True)
    run = lambda *c: subprocess.run([str(x) for x in c], cwd=root, check=True)
    common = ('-M', root / 'AndroidManifest.xml', '-S', root / 'res', '-I', a.android_jar,
              '--min-sdk-version', '4', '--target-sdk-version', '4',
              '--version-code', '3041', '--version-name', '3.4.1')
    run(aapt, 'package', '-f', '-m', '-J', out / 'gen', *common)
    srcs = sorted((root / 'java').rglob('*.java')) + sorted((out / 'gen').rglob('*.java'))
    run(javac, '-encoding', 'UTF-8', '-source', '8', '-target', '8', '-g:none', '-nowarn', '-Xlint:-options',
        '-bootclasspath', a.android_jar, '-d', out / 'classes', *srcs)
    run(java, '-cp', d8, 'com.android.tools.r8.D8', '--release', '--min-api', '9', '--lib', a.android_jar,
        '--output', out / 'dex', *sorted((out / 'classes').rglob('*.class')))
    unsigned, aligned, apk = out / 'unsigned.apk', out / 'aligned.apk', out / 'SolitaireCG.apk'
    run(aapt, 'package', '-f', '-c', 'es,en,mdpi,hdpi', *common, '-F', unsigned)
    with zipfile.ZipFile(unsigned, 'a', zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo('classes.dex', date_time=(1980, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, (out / 'dex/classes.dex').read_bytes())
    run(align, '-f', '4', unsigned, aligned)
    run(java, '-jar', signer, 'sign', '--ks', a.keystore, '--ks-key-alias', a.alias, '--ks-pass', 'file:' + a.storepass_file,
        '--min-sdk-version', '9', '--v1-signing-enabled', 'true', '--v2-signing-enabled', 'false', '--v3-signing-enabled', 'false',
        '--out', apk, aligned)
    run(java, '-jar', signer, 'verify', '--min-sdk-version', '9', apk)
    print('APK:', apk, apk.stat().st_size, 'bytes, SHA256', hashlib.sha256(apk.read_bytes()).hexdigest())

if __name__ == '__main__':
    main()
