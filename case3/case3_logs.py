import csv, io, os, re, sys, time, zipfile
from collections import Counter, defaultdict

args = sys.argv[1:]
LIMIT_MB = 120
MAX_N = None
if '--limit-mb' in args:
    LIMIT_MB = int(args[args.index('--limit-mb') + 1])
if '--max' in args:
    MAX_N = int(args[args.index('--max') + 1])
pos = [a for i, a in enumerate(args) if not a.startswith('--') and not (i > 0 and args[i - 1] in ('--limit-mb', '--max'))]
if not pos:
    print(__doc__)
    sys.exit(1)
MAX_READ = 25 * 1024 * 1024
FEAT = os.path.join(os.getcwd(), 'logs_features.csv')
OUT = os.path.join(os.getcwd(), 'logs_results.md')
out = []
try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass


def w(s=''):
    out.append(s)
    print(s)


def mask(t):
    t = re.sub(r'[\w.+-]+@[\w-]+\.[\w.]+', '<email>', t)
    t = re.sub(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', '<uuid>', t)
    t = re.sub(r'\b\d{1,3}(?:\.\d{1,3}){3}\b', '<ip>', t)
    t = re.sub(r'\b[A-Za-z0-9_\-]{24,}\b', '<tok>', t)
    t = re.sub(r'\d+', '<n>', t)
    return t.strip()[:140]


APP_PREFIX = re.compile(r'^\[[^\]]*\]\s+\S+\s+\d{4}-\d{2}-\d{2}T[\d:.]+\s+\[[A-Z]\]\s+')
VER = re.compile(r'Running on Os\.(\w+); OS version ([^;]+); App version (\S+)')
ERR_APP = re.compile(r'\s\[E\]\s|Exception|FATAL', re.I)

pairs = Counter()
err_tpl = Counter()
vpn_err_tpl = Counter()
feats = []
skipped = []
t0 = time.time()
z = zipfile.ZipFile(pos[0])
infos = sorted((i for i in z.infolist() if not i.is_dir()), key=lambda i: i.filename)
if MAX_N:
    infos = infos[::max(1, len(infos) // MAX_N)][:MAX_N]
w(f'# Результаты анализа логов ({time.strftime("%Y-%m-%d")})')
w('')
try:
    for n, info in enumerate(infos, 1):
        if n % 25 == 0:
            print(f'  {n}/{len(infos)} архивов, {time.time() - t0:.0f} с')
        parts = info.filename.split('/')
        folder = parts[1] if len(parts) > 2 else ''
        if info.file_size > LIMIT_MB * 1024 * 1024:
            skipped.append((info.filename, info.file_size))
            continue
        try:
            inner = zipfile.ZipFile(io.BytesIO(z.read(info)))
        except Exception:
            skipped.append((info.filename, info.file_size))
            continue
        f_ = dict(folder=folder, archive=parts[-1], n_log=0, n_txt=0, os='', os_version='', app_version='',
                  app_lines=0, app_error_lines=0, stack_traces=0, auth_verify=0,
                  access_lines=0, access_block=0, vpn_error_lines=0, vpn_refused=0)
        for m in inner.infolist():
            if m.is_dir():
                continue
            name = m.filename.strip().lower()
            is_app = name.endswith('.log')
            if is_app:
                f_['n_log'] += 1
            else:
                f_['n_txt'] += 1
            prev = []
            with inner.open(m) as fh:
                read = 0
                for raw in fh:
                    read += len(raw)
                    if read > MAX_READ:
                        break
                    line = raw.decode('utf-8', 'replace').rstrip()
                    if is_app:
                        f_['app_lines'] += 1
                        if not f_['app_version']:
                            mv = VER.search(line)
                            if mv:
                                f_['os'], f_['os_version'], f_['app_version'] = mv.group(1), mv.group(2).strip(), mv.group(3)
                        if 'StackTrace' in line:
                            f_['stack_traces'] += 1
                        if 'auth/verify' in line:
                            f_['auth_verify'] += 1
                        if ERR_APP.search(line):
                            f_['app_error_lines'] += 1
                            body = APP_PREFIX.sub('', line)
                            err_tpl[mask(body)] += 1
                            if prev:
                                pairs[(mask(prev[-1]), mask(body))] += 1
                        else:
                            body = APP_PREFIX.sub('', line)
                            if body.strip():
                                prev.append(body)
                                if len(prev) > 2:
                                    prev.pop(0)
                    elif 'access' in name:
                        f_['access_lines'] += 1
                        if '-> block]' in line:
                            f_['access_block'] += 1
                    else:
                        if '[Error]' in line or 'error' in name:
                            f_['vpn_error_lines'] += 1
                            if 'connection was refused' in line:
                                f_['vpn_refused'] += 1
                            vpn_err_tpl[mask(re.sub(r'^\d{4}/\d{2}/\d{2}\s+[\d:.]+\s+', '', line))] += 1
        feats.append(f_)
finally:
    cols = ['folder', 'archive', 'n_log', 'n_txt', 'os', 'os_version', 'app_version', 'app_lines', 'app_error_lines',
            'stack_traces', 'auth_verify', 'access_lines', 'access_block', 'vpn_error_lines', 'vpn_refused']
    with open(FEAT, 'w', encoding='utf-8-sig', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=cols, delimiter=';')
        wr.writeheader()
        wr.writerows(feats)

    w(f'Обработано вложенных архивов: {len(feats):,} из {len(infos):,}; пропущено (больше {LIMIT_MB} МБ или не открылись): {len(skipped)}')
    for nm, sz in skipped[:10]:
        w(f'- пропущен архив размером {sz / 1024 / 1024:.0f} МБ')
    w('')
    nf = len(feats)
    if nf:
        def share(pred):
            return round(100 * sum(1 for x in feats if pred(x)) / nf, 1)
        w('## Общая картина')
        w(f'- архивов с ошибками «connection was refused» в журнале VPN: {share(lambda x: x["vpn_refused"] > 0)} %')
        w(f'- архивов со стек-трейсами приложения: {share(lambda x: x["stack_traces"] > 0)} %')
        w(f'- архивов со строками ошибок [E]/Exception в журнале приложения: {share(lambda x: x["app_error_lines"] > 0)} %')
        w(f'- архивов с заблокированными соединениями (-> block): {share(lambda x: x["access_block"] > 0)} %')
        w('')

        def grp(key_fn, title, minimum=5):
            g = defaultdict(list)
            for x in feats:
                g[key_fn(x)].append(x)
            w(f'## {title}')
            w('| группа | архивов | % с connection refused | % со стек-трейсами | % с ошибками [E] |')
            w('|---|---|---|---|---|')
            for k, v in sorted(g.items(), key=lambda kv: -len(kv[1])):
                if len(v) < minimum:
                    continue
                c = len(v)
                w(f'| {k or "не определено"} | {c} | {round(100 * sum(1 for x in v if x["vpn_refused"] > 0) / c, 1)} | '
                  f'{round(100 * sum(1 for x in v if x["stack_traces"] > 0) / c, 1)} | '
                  f'{round(100 * sum(1 for x in v if x["app_error_lines"] > 0) / c, 1)} |')
            w('')
        grp(lambda x: x['os'], 'Ошибки по платформе')
        grp(lambda x: f"{x['os']} {x['os_version'].split('.')[0]}", 'Ошибки по версии ОС (основная версия)')
        grp(lambda x: x['app_version'], 'Ошибки по версии приложения')
    w('## Самые частые строки ошибок приложения (числа заменены на <n>)')
    for t, c in err_tpl.most_common(20):
        w(f'- {c:,} × {t}')
    w('')
    w('## Самые частые ошибки VPN-ядра')
    for t, c in vpn_err_tpl.most_common(15):
        w(f'- {c:,} × {t}')
    w('')
    w('## Что обычно происходит перед ошибкой в журнале приложения (предыдущая строка → строка ошибки)')
    for (a, b), c in pairs.most_common(20):
        w(f'- {c:,} × «{a}» → «{b}»')
    with open(OUT, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out))
    print('\nФайлы сохранены: ' + FEAT + ' и ' + OUT)
