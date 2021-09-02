from TikTokApi import TikTokApi #từ thư viện Tiktok API lấy ra đối tượng Tiktok API
import pprint
import json

api = TikTokApi.get_instance() #Khai báo API

results = 100 #Lưu số video cần lấy

trending = api.trending(count=results, custom_verifyFp="") #Lưu tất cả các json crawl về được, với mỗi json biểu diễn cho 1 video

dict_out={} #lưu file json là 1 từ điển chứa các file json nhỏ

for tiktok in trending:
    video_id = tiktok['id'] #gọi key (id)
    dict_out[video_id] = tiktok

with open('raw_data_day10.json', 'w', encoding='UTF8') as f:
    json.dump(dict_out, f, ensure_ascii=False, indent=4)


