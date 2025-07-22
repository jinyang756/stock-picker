import baostock as bs 

 # 登录系统 
lg = bs.login()
print(f"登录状态: {lg.error_code} - {lg.error_msg}")
