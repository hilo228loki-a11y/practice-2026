import pandas as pd

df = pd.read_csv('students.csv')
anomalies = []

for pid, group in df.groupby('ProcessInstanceId'):
    sorted_group = group.sort_values('EventIndex')
    acts = sorted_group['ActivityName'].tolist()

    rework_count = acts.count('Доработка заявки')
    if rework_count >= 2:
        anomalies.append({
            'ProcessInstanceId': pid,
            'AnomalyType': 'Множественный возврат на доработку',
            'Explanation': f'Заявка возвращалась на доработку {rework_count} раза, что указывает на критическое зацикливание процесса.'
        })

    if 'Заявка отменена' in acts and acts.index('Заявка отменена') > 3:
        anomalies.append({
            'ProcessInstanceId': pid,
            'AnomalyType': 'Поздняя отмена заявки',
            'Explanation': 'Заявка отменена на поздней стадии после прохождения согласования руководителем.'
        })

anomalies_df = pd.DataFrame(anomalies).drop_duplicates(subset=['ProcessInstanceId', 'AnomalyType'])
anomalies_df.to_csv('anomalies.csv', index=False, encoding='utf-8-sig')

print(f"Итоговый отбор: найдено критических аномалий — {len(anomalies_df)}")