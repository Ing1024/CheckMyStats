import requests
from bs4 import BeautifulSoup
import csv
import re

class DataCatcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
    
    def data_catch(self, url, save_csv_path):
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        tables = soup.find_all('table', class_='players_table bott bgs_table')

        if tables:
            all_data = []
            table_headers = []
            max_year = None  # 用于记录最大的年份
            
            for table in tables:
                rows = table.find_all('tr')
                
                # 提取表头（仅第一次）
                if not table_headers:
                    header_row = rows[1]
                    table_headers = [th.text.strip() for th in header_row.find_all('td')]
                    # 添加年份列到表头
                    table_headers[0] = '日期'  # 确保第一列是日期
                
                # 处理数据行
                data_rows = rows[2:]
                for row in data_rows:
                    cells = row.find_all('td')
                    row_data = [cell.text.strip() for cell in cells]
                    
                    # 检查是否是年份行（四位数字）
                    if re.match(r'^\d{4}$', row_data[0]):
                        current_year = int(row_data[0])
                        if max_year is None or current_year > max_year:
                            max_year = current_year
                        continue  # 跳过年份行
                    
                    # 处理有效数据行
                    if row_data and len(row_data) >= 7:  # 确保数据行有效
                        # 解析日期（格式如 04/09）
                        date_str = row_data[0]
                        if re.match(r'^\d{1,2}/\d{1,2}$', date_str):
                            month, day = map(int, date_str.split('/'))
                            
                            # 计算基础年份（最后一个年份 +1）
                            base_year = max_year + 1 if max_year else 2024
                            
                            # 根据月份确定年份
                            if 7 <= month <= 12:
                                year = base_year
                            else:
                                year = base_year + 1
                            
                            # 格式化为 YYYY-MM-DD
                            formatted_date = f"{year}-{month:02d}-{day:02d}"
                            row_data[0] = formatted_date  # 替换原日期
                            all_data.append(row_data)
            
            # 写入 CSV
            if all_data:
                with open(save_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(table_headers)
                    writer.writerows(all_data)
                print(f"数据已成功保存到 CSV 文件，基础年份为 {max_year + 1 if max_year else 2024}")
            else:
                print("未找到有效数据。")
        else:
            print("未找到任何表格，请检查网页结构或 class 名是否正确。")

if __name__== '__main__':
    catcher = DataCatcher()
    catcher.data_catch(url='https://nba.hupu.com/players/nikolajokic-4943.html', save_csv_path='data/nikola_jokic_game_stats.csv')