import requests
from bs4 import BeautifulSoup
import csv
import re

url = 'https://nba.hupu.com/players/lebronjames-650.html'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# 使用 find_all 获取所有符合条件的表格
tables = soup.find_all('table', class_='players_table bott bgs_table')

if tables:
    all_data = []
    table_headers = []
    for table in tables:
        rows = table.find_all('tr')
        # 提取表头（仅第一次）
        if not table_headers:
            header_row = rows[1]
            table_headers = [th.text.strip() for th in header_row.find_all('td')]
        # 提取数据行（跳过每个表格的表头行）
        data_rows = rows[2:]
        for row in data_rows:
            cells = row.find_all('td')
            row_data = [cell.text.strip() for cell in cells]

                 # 跳过以年份开头的行（四位数字，如 2004）
            if re.match(r'^\d{4}$', row_data[0]):  # 匹配纯四位数字的年份
                continue
            
            # 保留以日期开头的行（如 04/09）
            all_data.append(row_data)
    
    # 写入 CSV
    with open('lebron_james_all_stats.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(table_headers)
        writer.writerows(all_data)
    
    print("所有表格数据已成功保存到 lebron_james_all_stats.csv 文件中。")
else:
    print("未找到任何表格，请检查网页结构或 class 名是否正确。")