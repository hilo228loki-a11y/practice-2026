import pandas as pd

df = pd.read_csv('students.csv')

variants = []
for pid, group in df.groupby('ProcessInstanceId', sort=False):
    sorted_group = group.sort_values('EventIndex')
    activities = list(sorted_group['ActivityName'])
    variants.append(" > ".join(activities))

df_var = pd.DataFrame({'Route': variants})
var_counts = df_var['Route'].value_counts().reset_index()
var_counts.columns = ['Route', 'NumberOfCases']

total_cases = len(df_var)
var_counts['Share'] = var_counts['NumberOfCases'] / total_cases

var_counts.insert(0, 'Variant', [f"V{i+1}" for i in range(len(var_counts))])

var_counts.to_csv('variants.csv', index=False, encoding='utf-8-sig')
print("Таблица вариантов успешно сохранена!")


transitions = set()
for pid, group in df.groupby('ProcessInstanceId', sort=False):
    sorted_group = group.sort_values('EventIndex')
    acts = list(sorted_group['ActivityName'])
    for i in range(len(acts) - 1):
        transitions.add((acts[i], acts[i+1]))

df_trans = pd.DataFrame(list(transitions), columns=['SourceActivity', 'TargetActivity'])

df_trans.to_csv('student_transitions.csv', index=False, encoding='utf-8-sig')
print("Таблица переходов успешно сохранена!")