import csv, glob, os, sqlite3, sys, time

csv.field_size_limit(2**31 - 1)
args = sys.argv[1:]
REUSE = '--reuse' in args
LIMIT = None
if '--limit-rows' in args:
    LIMIT = int(args[args.index('--limit-rows') + 1])
pos = [a for i, a in enumerate(args) if not a.startswith('--') and not (i > 0 and args[i - 1] == '--limit-rows')]
ROOT = pos[0] if pos else 'db'
DBFILE = os.path.join(os.getcwd(), 'case3.sqlite')
OUT = os.path.join(os.getcwd(), 'case3_results.md')
out = []
try:
    sys.stdout.reconfigure(errors='replace')
except Exception:
    pass


def w(s=''):
    out.append(s)
    print(s)


def table(title, header, rows, note=None):
    w(f'### {title}')
    if note:
        w(note)
    w('')
    w('| ' + ' | '.join(header) + ' |')
    w('|' + '---|' * len(header))
    for r in rows:
        w('| ' + ' | '.join('' if v is None else (f'{v:,.2f}'.rstrip('0').rstrip('.') if isinstance(v, float) else (f'{v:,}' if isinstance(v, int) else str(v))) for v in r) + ' |')
    w('')


def pcts(vals, qs=(0.25, 0.5, 0.75, 0.9, 0.99)):
    v = sorted(vals)
    n = len(v)
    if not n:
        return [None] * len(qs)
    res = []
    for q in qs:
        k = q * (n - 1)
        lo = int(k)
        hi = min(n - 1, lo + 1)
        res.append(v[lo] + (v[hi] - v[lo]) * (k - lo))
    return res


def structure(table_name):
    p = os.path.join(ROOT, 'db_structure', table_name + '.csv')
    with open(p, encoding='utf-8-sig', newline='') as f:
        first = f.readline().strip()
    return [c.strip().strip('"') for c in first.split(';')]


def I(s):
    try:
        return int(s) if s != '' else None
    except ValueError:
        return None


def F(s):
    try:
        return float(s) if s != '' else None
    except ValueError:
        return None


def S(s):
    return s if s != '' else None


def T19(s):
    return s[:19] if s else None


def D10(s):
    return s[:10] if s else None


def B(s):
    return 1 if s.lower() in ('t', 'true', '1') else 0


def read_rows(path, header):
    with open(path, encoding='utf-8-sig', errors='replace', newline='') as f:
        rd = csv.reader(f, delimiter=';')
        if header:
            names = next(rd, [])
            yield names
        for i, r in enumerate(rd):
            if LIMIT and i >= LIMIT:
                break
            yield r


def load(con, tname, src, wanted, convs, ddl):
    t0 = time.time()
    cols = structure(src)
    idx = [cols.index(c) for c in wanted]
    need = max(idx)
    con.execute(f'DROP TABLE IF EXISTS {tname}')
    con.execute(ddl)
    ins = f'INSERT INTO {tname} VALUES ({",".join("?" * len(wanted))})'
    buf, n, bad = [], 0, 0
    for r in read_rows(os.path.join(ROOT, src + '.csv'), False):
        if len(r) <= need:
            bad += 1
            continue
        buf.append([cv(r[i]) for cv, i in zip(convs, idx)])
        n += 1
        if len(buf) >= 100000:
            con.executemany(ins, buf)
            buf = []
    if buf:
        con.executemany(ins, buf)
    con.commit()
    w(f'- {tname}: загружено {n:,} строк за {time.time() - t0:.0f} с (пропущено коротких: {bad})')


def load_ucl(con):
    t0 = time.time()
    con.execute('DROP TABLE IF EXISTS ucl')
    con.execute('CREATE TABLE ucl (user_id INTEGER, day TEXT, sub INTEGER)')
    subs = set()
    files = sorted(glob.glob(os.path.join(ROOT, 'user_connection_logs_*.csv')))
    total = 0
    for fp in files:
        gen = read_rows(fp, True)
        names = next(gen)
        iu, ic, isub = names.index('user_id'), names.index('created_at'), names.index('subscribe_id')
        buf = []
        for r in gen:
            if len(r) <= max(iu, ic, isub):
                continue
            sv = r[isub]
            if sv != '':
                subs.add(sv)
            buf.append((I(r[iu]), D10(r[ic]), 1 if sv != '' else 0))
            if len(buf) >= 200000:
                con.executemany('INSERT INTO ucl VALUES (?,?,?)', buf)
                total += len(buf)
                buf = []
        if buf:
            con.executemany('INSERT INTO ucl VALUES (?,?,?)', buf)
            total += len(buf)
        con.commit()
        print(f'  {os.path.basename(fp)} готов, всего строк {total:,}')
    w(f'- ucl (журналы подключений, {len(files)} файлов): загружено {total:,} строк за {time.time() - t0:.0f} с')
    return subs


def build(con):
    w('## 0. Загрузка данных')
    con.execute('PRAGMA journal_mode=OFF')
    con.execute('PRAGMA synchronous=OFF')
    load(con, 'users', 'users', ['id', 'created_at', 'trial_used_at'], [I, T19, T19],
         'CREATE TABLE users (id INTEGER, created_at TEXT, trial_used_at TEXT)')
    load(con, 'orders', 'orders', ['user_id', 'product_id', 'amount', 'status', 'created_at', 'trial'],
         [I, I, F, S, T19, B],
         'CREATE TABLE orders (user_id INTEGER, product_id INTEGER, amount REAL, status TEXT, created_at TEXT, trial INTEGER)')
    load(con, 'subscribe', 'subscribe', ['id', 'user_id', 'product_id', 'created_at'], [I, I, I, T19],
         'CREATE TABLE subscribe (id INTEGER, user_id INTEGER, product_id INTEGER, created_at TEXT)')
    load(con, 'devices', 'devices', ['user_id', 'device_identifier'], [I, S],
         'CREATE TABLE devices (user_id INTEGER, device_identifier TEXT)')
    load(con, 'sessions', 'sessions', ['user_id', 'ip_address'], [I, S],
         'CREATE TABLE sessions (user_id INTEGER, ip_address TEXT)')
    load(con, 'adv', 'adv_view_history', ['user_id', 'created_at'], [I, D10],
         'CREATE TABLE adv (user_id INTEGER, day TEXT)')
    subs = load_ucl(con)
    t0 = time.time()
    for ddl in [
        'CREATE UNIQUE INDEX IF NOT EXISTS ix_users ON users(id)',
        'CREATE INDEX IF NOT EXISTS ix_orders ON orders(user_id)',
        'CREATE INDEX IF NOT EXISTS ix_dev ON devices(user_id)',
        'DROP TABLE IF EXISTS ud',
        'CREATE TABLE ud AS SELECT user_id, day, count(*) conns, max(sub) has_sub FROM ucl WHERE user_id IS NOT NULL AND day IS NOT NULL GROUP BY user_id, day',
        'CREATE UNIQUE INDEX ix_ud ON ud(user_id, day)',
        'DROP TABLE IF EXISTS advd',
        'CREATE TABLE advd AS SELECT user_id, day, count(*) views FROM adv WHERE user_id IS NOT NULL AND day IS NOT NULL GROUP BY user_id, day',
        'CREATE UNIQUE INDEX ix_advd ON advd(user_id, day)',
    ]:
        con.execute(ddl)
    con.commit()
    con.execute('DROP TABLE IF EXISTS meta_subs')
    con.execute('CREATE TABLE meta_subs (id TEXT)')
    con.executemany('INSERT INTO meta_subs VALUES (?)', [(s,) for s in subs])
    con.commit()
    w(f'- индексы и агрегаты построены за {time.time() - t0:.0f} с')
    w('')


def h3(con):
    w('## Гипотеза 3. Срок до покупки и роль пробного периода')
    q = con.execute
    n_users = q('SELECT count(*) FROM users').fetchone()[0]
    table('Заказы по статусу и признаку пробного периода',
          ['status', 'trial', 'заказов', 'пользователей', 'средняя сумма'],
          q('SELECT status, trial, count(*), count(DISTINCT user_id), round(avg(amount),1) FROM orders GROUP BY 1,2 ORDER BY 3 DESC').fetchall(),
          'Оплаченным считается заказ со статусом paid; trial=1 — заказ пробного периода.')
    q('DROP TABLE IF EXISTS pu')
    q("""CREATE TABLE pu AS SELECT user_id,
          min(CASE WHEN status='paid' THEN created_at END) first_paid,
          min(CASE WHEN status='paid' AND trial=1 THEN created_at END) first_trial,
          min(CASE WHEN status='paid' AND trial=0 THEN created_at END) first_full
         FROM orders WHERE user_id IS NOT NULL GROUP BY user_id""")
    q('CREATE UNIQUE INDEX ix_pu ON pu(user_id)')
    q('DROP TABLE IF EXISTS seg')
    q("""CREATE TABLE seg AS SELECT u.id user_id, u.created_at reg, u.trial_used_at, p.first_paid, p.first_trial, p.first_full,
          CASE WHEN p.first_paid IS NULL THEN '1. нет оплат'
               WHEN p.first_trial IS NOT NULL AND p.first_full IS NULL THEN '2. только пробный период'
               WHEN p.first_trial IS NOT NULL AND p.first_full >= p.first_trial THEN '3. пробный, затем полная оплата'
               WHEN p.first_trial IS NULL THEN '4. полная оплата без пробного'
               ELSE '5. полная оплата до пробного' END segment
         FROM users u LEFT JOIN pu p ON p.user_id=u.id""")
    q('CREATE INDEX ix_seg ON seg(user_id)')
    con.commit()
    rows = q('SELECT segment, count(*) FROM seg GROUP BY 1 ORDER BY 1').fetchall()
    paid_total = sum(c for s, c in rows if not s.startswith('1.'))
    table('Пользователи по пути к оплате', ['сегмент', 'пользователей', '% от всех', '% от платящих'],
          [(s, c, round(100 * c / n_users, 2), None if s.startswith('1.') else round(100 * c / paid_total, 1)) for s, c in rows])
    data = q('SELECT segment, julianday(first_paid)-julianday(reg) FROM seg WHERE first_paid IS NOT NULL AND reg IS NOT NULL').fetchall()
    neg = sum(1 for s, d in data if d < 0)
    by = {}
    for s, d in data:
        if d >= 0:
            by.setdefault(s, []).append(d)
            by.setdefault('все платящие', []).append(d)
    res = []
    for s in sorted(by):
        p = pcts(by[s])
        res.append((s, len(by[s])) + tuple(round(x, 2) for x in p))
    table('Дней от регистрации до первой оплаты (включая пробный период)',
          ['сегмент', 'пользователей', 'p25', 'медиана', 'p75', 'p90', 'p99'], res,
          f'Исключены оплаты раньше регистрации (ошибка данных): {neg:,}.')
    allv = by.get('все платящие', [])
    buckets = [('в день регистрации (<1 дня)', 0, 1), ('1–3 дня', 1, 3), ('3–7 дней', 3, 7), ('7–30 дней', 7, 30), ('30–90 дней', 30, 90), ('более 90 дней', 90, 1e9)]
    table('Распределение срока до первой оплаты', ['срок', 'пользователей', '%'],
          [(n, sum(1 for d in allv if a <= d < b), round(100 * sum(1 for d in allv if a <= d < b) / len(allv), 1) if allv else None) for n, a, b in buckets])
    lag = [d for (d,) in q("SELECT julianday(first_full)-julianday(first_trial) FROM seg WHERE segment LIKE '3.%'").fetchall() if d is not None]
    table('Дней от пробного периода до полной оплаты (сегмент 3)', ['пользователей', 'p25', 'медиана', 'p75', 'p90'],
          [(len(lag),) + tuple(round(x, 2) for x in pcts(lag, (0.25, 0.5, 0.75, 0.9)))] if lag else [])
    table('Согласованность признаков пробного периода', ['показатель', 'пользователей'], [
        ('trial_used_at заполнен', q('SELECT count(*) FROM seg WHERE trial_used_at IS NOT NULL').fetchone()[0]),
        ('есть оплаченный заказ с trial=1', q('SELECT count(*) FROM seg WHERE first_trial IS NOT NULL').fetchone()[0]),
        ('оба признака', q('SELECT count(*) FROM seg WHERE trial_used_at IS NOT NULL AND first_trial IS NOT NULL').fetchone()[0]),
        ('trial_used_at пуст, но был заказ trial=1', q('SELECT count(*) FROM seg WHERE trial_used_at IS NULL AND first_trial IS NOT NULL').fetchone()[0]),
    ])
    table('Первая оплата по тарифам (оплаченных заказов)', ['product_id', 'заказов'],
          q("SELECT product_id, count(*) FROM orders WHERE status='paid' GROUP BY 1 ORDER BY 2 DESC").fetchall())


def h1(con):
    w('## Гипотеза 1. Повторные аккаунты ради пробного периода')
    q = con.execute
    n_trial = q('SELECT count(*) FROM users WHERE trial_used_at IS NOT NULL').fetchone()[0]
    q('DROP TABLE IF EXISTS dev')
    q("CREATE TABLE dev AS SELECT DISTINCT user_id, device_identifier FROM devices WHERE user_id IS NOT NULL AND device_identifier IS NOT NULL AND device_identifier<>''")
    q('CREATE INDEX ix_dev2 ON dev(device_identifier)')
    q('DROP TABLE IF EXISTS dg')
    q("""CREATE TABLE dg AS SELECT d.device_identifier, count(*) n_users, sum(u.trial_used_at IS NOT NULL) n_trial,
          min(u.created_at) first_reg, max(u.created_at) last_reg
         FROM dev d JOIN users u ON u.id=d.user_id GROUP BY 1""")
    q('CREATE INDEX ix_dg ON dg(device_identifier)')
    con.commit()
    w(f'Пользователей с использованным пробным периодом: {n_trial:,}.')
    w('')
    table('Сколько аккаунтов приходится на одно устройство (по device_identifier)',
          ['аккаунтов на устройстве', 'устройств', 'аккаунтов', 'из них с пробным периодом'],
          q("""SELECT CASE WHEN n_users=1 THEN '1' WHEN n_users=2 THEN '2' WHEN n_users=3 THEN '3' WHEN n_users<=5 THEN '4–5'
                WHEN n_users<=10 THEN '6–10' ELSE '11 и более' END g, count(*), sum(n_users), sum(n_trial)
               FROM dg GROUP BY g ORDER BY min(n_users)""").fetchall(),
          'Идентификаторы с 11 и более аккаунтами могут быть эмуляторами или общими значениями по умолчанию, их лучше исключать из кандидатов.')
    cand = q('SELECT count(*), sum(n_users), sum(n_trial) FROM dg WHERE n_trial>=2 AND n_users<=10').fetchone()
    uniq = q("""SELECT count(DISTINCT d.user_id) FROM dev d JOIN dg ON dg.device_identifier=d.device_identifier
                JOIN users u ON u.id=d.user_id WHERE dg.n_trial>=2 AND dg.n_users<=10 AND u.trial_used_at IS NOT NULL""").fetchone()[0]
    table('Кандидаты: устройства, на которых пробным периодом воспользовались 2 и более аккаунта (до 10 аккаунтов на устройство)',
          ['устройств', 'аккаунтов на них', 'аккаунтов с пробным периодом (по устройствам)', 'уникальных пользователей с пробным', '% от всех пробных'],
          [(cand[0], cand[1], cand[2], uniq, round(100 * uniq / n_trial, 2) if n_trial else None)])
    spans = [d for (d,) in q("SELECT julianday(last_reg)-julianday(first_reg) FROM dg WHERE n_trial>=2 AND n_users<=10").fetchall() if d is not None]
    table('Интервал между первой и последней регистрацией на устройстве-кандидате, дней', ['устройств', 'p25', 'медиана', 'p75', 'p90'],
          [(len(spans),) + tuple(round(x, 2) for x in pcts(spans, (0.25, 0.5, 0.75, 0.9)))] if spans else [])
    cov = q('SELECT count(*) FROM users u WHERE u.trial_used_at IS NOT NULL AND EXISTS (SELECT 1 FROM dev d WHERE d.user_id=u.id)').fetchone()[0]
    table('Покрытие: у скольких пользователей с пробным периодом есть запись об устройстве', ['пользователей', 'с устройством', '%'],
          [(n_trial, cov, round(100 * cov / n_trial, 1) if n_trial else None)])
    
    q('DROP TABLE IF EXISTS sip')
    q('CREATE TABLE sip AS SELECT DISTINCT user_id, ip_address FROM sessions WHERE user_id IS NOT NULL AND ip_address IS NOT NULL')
    q('CREATE INDEX ix_sip ON sip(ip_address)')
    q('DROP TABLE IF EXISTS ig')
    q('CREATE TABLE ig AS SELECT s.ip_address, count(*) n_users, sum(u.trial_used_at IS NOT NULL) n_trial FROM sip s JOIN users u ON u.id=s.user_id GROUP BY 1')
    con.commit()
    ipc = q('SELECT count(*), sum(n_users), sum(n_trial) FROM ig WHERE n_trial>=3 AND n_users<=20').fetchone()
    table('Слабый сигнал: IP-адреса с 3 и более пробными аккаунтами (до 20 аккаунтов на адрес)',
          ['адресов', 'аккаунтов на них', 'пробных аккаунтов'], [tuple(ipc)],
          'Один IP может принадлежать провайдеру или офису (общий NAT), поэтому это только дополнительный признак к устройству.')


def h2(con):
    w('## Гипотеза 2. Лимиты бесплатного тарифа (косвенная оценка)')
    w('Объёма трафика в данных нет. Используются косвенные признаки: интенсивность подключений бесплатных пользователей и просмотры рекламы (по описанию задачи, реклама нужна для расширения лимита). Бесплатным считается пользователь-день, в который ни у одного подключения нет subscribe_id (предположение).')
    w('')
    q = con.execute
    for flag, name in ((0, 'бесплатные'), (1, 'с подпиской')):
        v = [c for (c,) in q('SELECT conns FROM ud WHERE has_sub=?', (flag,)).fetchall()]
        n_users = q('SELECT count(DISTINCT user_id) FROM ud WHERE has_sub=?', (flag,)).fetchone()[0]
        p = pcts(v)
        table(f'Подключений за день на пользователя: {name}', ['пользователь-дней', 'пользователей', 'p25', 'медиана', 'p75', 'p90', 'p99'],
              [(len(v), n_users) + tuple(round(x, 1) for x in p)] if v else [])
    tot, withad = q("""SELECT count(*), sum(a.views IS NOT NULL) FROM ud LEFT JOIN advd a ON a.user_id=ud.user_id AND a.day=ud.day
                       WHERE ud.has_sub=0""").fetchone()
    views = [x for (x,) in q("""SELECT a.views FROM ud JOIN advd a ON a.user_id=ud.user_id AND a.day=ud.day WHERE ud.has_sub=0""").fetchall()]
    p = pcts(views, (0.5, 0.75, 0.9, 0.99))
    table('Просмотры рекламы в дни активности бесплатных пользователей', ['пользователь-дней', 'из них с рекламой', '% с рекламой', 'просмотров в такой день: медиана', 'p75', 'p90', 'p99'],
          [(tot, withad or 0, round(100 * (withad or 0) / tot, 2) if tot else None) + tuple(round(x, 1) for x in p)])
    table('По месяцам: бесплатные пользователи и доля тех, кто смотрел рекламу',
          ['месяц', 'активных бесплатных пользователей', 'из них смотрели рекламу', '% пользователей', 'пользователь-дней', 'с рекламой, %'],
          [(m, fu, ua, round(100 * ua / fu, 1) if fu else None, ud, round(100 * da / ud, 1) if ud else None) for m, fu, ua, ud, da in q(
              """SELECT substr(ud.day,1,7), count(DISTINCT ud.user_id), count(DISTINCT CASE WHEN a.views IS NOT NULL THEN ud.user_id END),
                        count(*), sum(a.views IS NOT NULL)
                 FROM ud LEFT JOIN advd a ON a.user_id=ud.user_id AND a.day=ud.day WHERE ud.has_sub=0 GROUP BY 1 ORDER BY 1""").fetchall()])
    ids = {r[0] for r in q('SELECT id FROM meta_subs').fetchall()}
    real = {str(r[0]) for r in q('SELECT id FROM subscribe').fetchall()}
    table('Проверка допущения: subscribe_id из журналов подключений существует в таблице subscribe',
          ['различных subscribe_id в журналах', 'найдено в subscribe', '%'],
          [(len(ids), len(ids & real), round(100 * len(ids & real) / len(ids), 1) if ids else None)])


def logs_link(con):
    path = os.path.join(os.getcwd(), 'logs_features.csv')
    if not os.path.exists(path):
        return
    w('## Гипотеза 4 (связь логов с БД)')
    con.execute('DROP TABLE IF EXISTS lf')
    con.execute('CREATE TABLE lf (folder INTEGER, archive TEXT, app_error_lines INTEGER, vpn_refused INTEGER, stack_traces INTEGER)')
    rows = []
    with open(path, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f, delimiter=';'):
            rows.append((I(r['folder']), r['archive'], I(r['app_error_lines']) or 0, I(r['vpn_refused']) or 0, I(r['stack_traces']) or 0))
    con.executemany('INSERT INTO lf VALUES (?,?,?,?,?)', rows)
    con.commit()
    q = con.execute
    total = q('SELECT count(DISTINCT folder) FROM lf WHERE folder IS NOT NULL').fetchone()[0]
    in_users = q('SELECT count(DISTINCT folder) FROM lf WHERE folder IN (SELECT id FROM users)').fetchone()[0]
    in_conn = q('SELECT count(DISTINCT folder) FROM lf WHERE folder IN (SELECT DISTINCT user_id FROM ud)').fetchone()[0]
    table('Проверка: числовое имя каталога логов — это user_id?', ['каталогов', 'есть в users.id', '% ', 'есть среди user_id журналов подключений'],
          [(total, in_users, round(100 * in_users / total, 1) if total else None, in_conn)])
    table('Ошибки в логах по сегменту пользователя', ['сегмент', 'архивов', 'с ошибкой connection refused, %', 'со стек-трейсами, %'],
          [(s, n, round(100 * r / n, 1), round(100 * st / n, 1)) for s, n, r, st in q(
              """SELECT s.segment, count(*), sum(lf.vpn_refused>0), sum(lf.stack_traces>0) FROM lf JOIN seg s ON s.user_id=lf.folder GROUP BY 1 ORDER BY 1""").fetchall()])


def main():
    if not os.path.isdir(ROOT):
        print(__doc__)
        sys.exit(1)
    w(f'# Результаты анализа кейса 3 ({time.strftime("%Y-%m-%d")})')
    w('')
    first = not (REUSE and os.path.exists(DBFILE))
    con = sqlite3.connect(DBFILE)
    try:
        if first:
            build(con)
        else:
            w('Использована готовая case3.sqlite (--reuse).')
            w('')
        h3(con)
        h1(con)
        h2(con)
        logs_link(con)
    except Exception as e:
        import traceback
        w(f'ОШИБКА: {type(e).__name__}: {e}')
        w('```')
        w(traceback.format_exc())
        w('```')
    finally:
        with open(OUT, 'w', encoding='utf-8') as f:
            f.write('\n'.join(out))
        print('\nФайл сохранён: ' + OUT)


if __name__ == '__main__':
    main()
