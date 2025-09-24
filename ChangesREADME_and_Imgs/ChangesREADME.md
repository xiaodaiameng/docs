# 改动：

## 一、前端

### （前端代码全部在FinancialCareerCommunity\frontend）

### 1，frontend\金融就业服务系统\finance-employment\src\router\index.js

```
   meta: {

​    requiresAuth: true

   }
```





![image-20250924134906311](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\1.png)

```
   meta: {

​    requiresAuth: false

   }

  },

  {

   path: '/register',

   name: 'Register',

   component: () => import('../views/Register/index.vue'),

   meta: {

​    requiresAuth: false

   }

  },

 ],

})
```

![image-20250924135026523](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\2.png)

```
// 路由守卫

router.beforeEach((to, from, next) => {

 // 检查是否需要认证

 if (to.meta.requiresAuth) {

  // 获取本地存储的token

  const token = localStorage.getItem('token')

  // 如果有token，继续访问

  if (token) {

   next()

  } else {

   // 如果没有token，重定向到登录页面

   next({ name: 'Login' })

  }

 } else {

  // 不需要认证的页面直接访问

  next()

 }
```

![image-20250924135054577](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\image-20250924135054577.png)

### 2，frontend\金融就业服务系统\finance-employment\src\views\Login\index.vue



```
import { RouterLink, useRouter } from 'vue-router';
```

![image-20250924135400249](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\4.png)

```
import { ref } from 'vue';
import axios from 'axios';

const router = useRouter();

// 表单数据
const form = ref({
  username: '',
  password: '',
  remember: false
});

// 表单验证规则
const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少为6位', trigger: 'blur' }
```

![image-20250924135433709](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\5.png)

```
  ]
};

// 登录方法
const handleLogin = async () => {
  try {
    // 发送登录请求到FastAPI后端
    const response = await axios.post('http://localhost:8080/api/auth/login',
      new URLSearchParams({
        username: form.value.username,
        password: form.value.password
      }),
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    );
    // 登录成功，保存token
```

![image-20250924135518674](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\6.png)

```
const token = response.data.access_token;
localStorage.setItem('token', token);

// 设置axios默认请求头，以便后续请求自动携带token
axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

// 跳转到首页
router.push('/');
} catch (error) {
    // 登录失败，显示错误信息
    if (error.response && error.response.status === 401) {
      alert('用户名或密码错误');
    } else {
      alert('登录失败，请稍后重试');
      console.error('登录错误:', error);
    }
  }
};
```

![image-20250924135538813](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\7.png)

                <el-form ref="loginForm" :model="form" :rules="rules" class="login-form"  label-position="right" label-width = "40px" status-icon>
                    <el-form-item prop="username" label="账户">
                        <el-input v-model="form.username" placeholder="请输入用户名"/>
    
                    <el-form-item prop="password" label="密码">
                        <el-input v-model="form.password" type="password" placeholder="请输入密码" />

![image-20250924140445384](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\8.png)

```
<el-checkbox v-model="form.remember" class="checkbox">
```

    <el-button @click="handleLogin" class="button" size="large" type="primary">开始找工作</el-button>
    <div style="margin-top: 10px; text-align: center;">
    	<RouterLink to="/register">还没有账号？立即注册</RouterLink>
     </div>

![image-20250924140631551](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\9.png)

### 3，在frontend\金融就业服务系统\finance-employment\src\views下创建文件夹Register及之下的注册文件index.vue

### 4，frontend\金融就业服务系统\finance-employment\src\views\Home\Components\HomeBanner.vue替换了内容。

## 二、后端

### 1，创建数据库迁移工具env.py到文件夹alembic

- 该文件夹内部的一些文件是在终端输入一些命令下载才产生的。

创建初始迁移，在命令行输入：

```
alembic revision --autogenerate -m Initial migration
```

成功后，在命令行输入以下命令来应用这个初始迁移文件，创建数据库表：

```
alembic upgrade head
```

- 但是之后失败了，所以重置过......比较乱，不展开。

### 2，test下新增了一测试脚本，根目录新建了create_db.py和create_users_table_direct.py

### 3，auth_service.py和token_blacklist.py从app/services，移动到了app/services/auth

### 4，app/deps/sql下的get_db()被删去了，直接使用了app/core/sql下的get_db()

### 5，多个文件被修改，难以记录。

### 6，app/main.py

```
    uvicorn.run(app, host=config.host, port=config.port)
```

改为：

```
uvicorn.run("app.main:app", host=config.host, port=config.port, reload=True)
```

### 7，auth_service.py的改变

![image-20250924171550007](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\11.png)

## 三、运行与关闭

### 1，运行：使用两个独立终端同时运行前后端服务

（一般习惯先开后端后开前端）

- 后端：

通过 Python 的 `-m` 参数运行 `app/main.py` 模块（因为该模块中已经写了启动代码）：

```
python -m app.main
```

或调用 `uvicorn` 命令行工具，指定应用入口（app/main.py中的 app实例）（最常用）：

```
 uvicorn app.main:app --reload --port 8080
```

或通过 `python -m` 调用 `uvicorn` 模块，再同二一样。

```
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

- 前端：

先打开前端目录：

```
cd d:\PythonCode\PyCrawler\FinancialCareerCommunity\frontend\金融就业服务系统\finance-employment
```

再：

```
npm run dev
```



两个都运行正确后：

- 访问网址 ：访问 http://localhost:5173 （或启动更多个端口，5174，5175 等，均可访问。）
- 后端已在 config.py 中配置了非常宽松的 CORS 策略，允许前端端口正常访问后端（8080）的API。



### 2，关闭

关闭整个服务，可以先关闭后端，直接多按几个Ctrl+C结束，

前端端口要关闭时，不能直接Ctrl+C，否则下次开启将是5174，再下次将是5175，...（虽然都能访问）

需要输入：

```
taskkill /f /im node.exe 
```

终止所有Node.js进程



## 四、碎片

1. 运行前提是 pip install了各种东西。

2. 前端这个文件我忘记在哪里的了，不确定有没有被ai改动过。

![image-20250924160821878](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\12.png)

3. 目录：里面这个README.md 没改。

   cookies 和 crawler_data 不重要可删。

**![image-20250924235742112](C:\Users\Yao\AppData\Roaming\Typora\typora-user-images\13.png)**

## to be continue...



