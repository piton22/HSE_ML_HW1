def extract_torque_rpm(col):

    col = str(col)

    # Разделение строки на части
    if 'at' in col:
        parts = col.split('at')

    else:
        parts = col.split('@')

    if len(parts) == 1:
        return None, None

    torque_part = parts[0].replace(',','.').strip()
    rpm_part = parts[1].replace(',','').strip()


    # Оставим только числовые символы и разделители
    torque_part = ''.join(filter(lambda c: c.isdigit() or c == '.', torque_part))
    rpm_part = ''.join(filter(lambda c: c.isdigit() or c == '.' or c=='-' or c=='~' , rpm_part))

    # Получим значение torque с учетом единиц измерения
    if 'kgm' in str(col) or 'kg*m' in str(col):
        torque_value = float(torque_part) * 9.8
    else:
        torque_value = float(torque_part)

    # Получим значение rpm. Если указан интервал, то берем среднее
    if '-' in rpm_part:
        rpm_values = rpm_part.split('-')
        rpm_min = float(rpm_values[0])
        rpm_max = float(rpm_values[1])
        rpm_value = (rpm_min + rpm_max) / 2

    elif '~' in rpm_part:
        rpm_values = rpm_part.split('~')
        rpm_min = float(rpm_values[0])
        rpm_max = float(rpm_values[1])
        rpm_value = (rpm_min + rpm_max) / 2
    else:
        rpm_value = float(rpm_part)


    return torque_value, rpm_value