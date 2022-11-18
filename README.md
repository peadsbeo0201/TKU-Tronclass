TKU Tronclass
===

登入
---
> #### 破解SSO單一登入驗證碼，獲取Session Cookie，將驗證資訊注入Tronclass封包中。

數字點名
---
> #### 監聽點名的roll call封包，獲取roll call id，向Server發送大量數字點名封包進行破解。


使用方法
---
> ```python
> from tronclass import Tronclass
> client = Tronclass('學號', '密碼')
> client.run()
> ```