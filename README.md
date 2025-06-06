
需求：一个小的软件团队（3个成员）能把这个 “电梯调度测试框架” 项目完整地创建出来，成为一个开源项目，具体要求是：

1）用开源的方式，把这个项目的测试框架写出来

2）用开源的方式，实现几个经典的算法 （下文提到的 bus / taxi / 正常调度算法）

3）用开源的方式，把项目的可视化做出来。就是用 GUI 的方式，可以接上不同学生的调度算法，通过 GUI 的方式，看到各个算法的优劣。 

期待的用户是：有一年以上编程经验的大学生，或者 IT 职业人士。 

用户测试包括：

1）用户可以阅读到清晰的需求描述， API 描述 （文档），依据这个 API 写的测试框架，可以很方便地运行这个框架，选取一组测试数据来测试某个电梯调度算法。 

2）用户可以选取一个算法，用测试框架来运行这个算法。

3）用户可以在文档的指导下，用一种新的语言来实现电梯调度算法，这个算法能够被测试框架加载并测试，并可以以 GUI 的方式看到算法运行的过程和结果。 

以前的需求文档
现代软件工程 结对编程 (II) 电梯调度

Pair Project II: Elevator Scheduler

<现代软件工程> 的结对编程作业,  作者: 邹欣

- 怎样设计API?  怎样从不同角度考虑需求?  怎样对不同的设计进行评估? 
- 怎样做设计一个测试框架来测试众多解决方案?  如何用 “真实” 的数据来驱动的测试，判定算法在各种情况下的优劣?
- 怎样把各种算法模块用松耦合的方式集成，用 GUI 显示运行状态？
- 测试框架， 算法， GUI 显示都由不同的人来实现，但是大家通过 API，能顺利集成为一个可运行的软件？
- 怎样和伙伴合作,  有效交流，解决分歧，达到共识，合理分工，快速有效地完成这些挑战?
电梯作业的挑战和参考
这道题目在过去的10年中给不少同学造成了麻烦，一些助教也觉得不好改这个作业，下面是我对这个作业的一些认识，给学生/助教/老师做参考。

首先对于这个作业，有四种角色，她们的需求未必一致：

-       老师：希望作业能真正锻炼同学们的软件工程能力

-       助教：希望作业好改，分数有区分度，容易分清好学生和差学生，很容易抓到抄袭

-       学生：希望作业容易，打分公平，有意思，能学到一些有用的技能

-       其他读者：希望能给自己的教学/工作/学习有一些参考

前三类角色的需求是这个作业的重点。这个作业就是要学生写一个“电梯调度程序”， 助教写一个“电梯调度程序的测试框架”。流程如下：

老师宣布作业，讲解作业的背景，要求，软件工程的相关理论。
助教把技术文档交给学生，把测试框架连同简单的测试数据也交给学生
学生阅读技术文档，试运行测试框架，写自己的调度程序，上交自己的调度程序给助教。
助教设计各种新的测试数据，测试学生的调度程序能否满足
基本要求：所有乘客最后都能送到目的地
效能要求：测试程序的KPI,
            并以上面结果给学生作业成绩排序。

        5. 学生可以做进一步作业（例如实现一个GUI 的电梯运行显示界面），写博客描述自己程序的特点以及学到的软件工程技能。

        6. 助教给学生打分，并通过博客留言等方式交流。

        7. 老师总结并让同学互相交流

这个作业对学生和助教有什么挑战呢？ 下面一一说来：

挑战1.  什么是好的调度算法？

当然第一是所有的乘客最后都到了目的地

第二，效率最高：

    -       等候时间最短？

    -       在电梯里的时间最短？

    -       …?

建议：电梯调度有几种极端的情况：

    -       公共汽车（bus）： 像公共汽车一样，每站都停，到头了，就向反方向走. 

    -       出租车模式（taxi）: 只接受一个请求，然后就直奔目标，中途顺路的请求都一概不理。

    -       正常的电梯：比出租车能接受更多顺路请求，但是不像公共汽车每站都停，来回奔忙。

经过几次的讨论，大家都认为是“所有乘客的平均旅行时间（包括等待电梯，在电梯内的旅行时间）”是一个最合适的KPI。 这个平均旅行时间还可以是加权的， 例如，

乘客A 从 1 楼到 2 楼， 乘客B 从3 楼到 20 楼

结果在调度系统方案甲中，这两位乘客都花了 10 分钟 （等待+旅行），乘客A 的不满情绪应该大大地高于乘客B，对吧？ 

在调度系统方案乙中，乘客A 花了 4 分钟，乘客B 花了 16 分钟。

方案甲乙的平均旅行时间是一样的，如果我们调查乘客A和B 对于电梯调度系统的满意程度， 我们得到的满意程度会是一样么？如何改进KPI？

挑战2. 测试框架给学生的接口是什么？

电梯调度程序只是电梯+乘客系统的一部分， 那么同学要完成这一部分的工作，这部分的工作怎么和其他部分整合呢？是写一个 .cpp 文件去实现某一些类，还是…?

建议：

第一步，可以是和语言有关的， 例如老师提供了一个 bus 模式的实现，用CPP 完成，然后学生改写其中的类的实现，规定不能改变 .h 或其他的模块。

第二步，可以是和语言无关的接口。 例如，不同的学生小组用 C++，Java，C#，Python 等程序都能和测试框架交流，完成电梯调度任务。 

挑战3. 调度模块能做什么？

很多学生一开始就想自己实现所有电梯的模块，然后调度模块直接修改各个电梯的位置，直到所有乘客都到达目的地。

老师问：那如果模块有bug，电梯运行速度超过合理范围，助教如何发现呢？

学生答：嗯… 助教写一个分析程序，分析各种log，找到不合理的地方。

老师问：那不同的学生的调度逻辑都不同，助教怎么能有足够的知识和判断在事后写程序来分析呢？

学生：反正这样我比较爽，其他人我不管。

老师: …

建议：

测试框架要管理整个电梯系统的运行，和乘客模块的交互，以及各种计时和统计。

电梯调度模块能知道当前各个电梯的位置，以及系统的情况。调度模块输出的，是给各个电梯发出的运行指令。

挑战4. 如何模拟数据？

电梯系统的数据：

        楼层的情况，电梯的数量，每个电梯运行速度，载客重量和人数的上限，电梯能到达的楼层

乘客数据：准备一个数据文件，每个数据有下面的格式：

乘客ID，乘客体重，乘客出现的楼层，乘客的目的地楼层，乘客源楼层的时间。

那么，电梯调度模块能读这个数据文件么？

很多同学觉得这样很简单，让电梯调度模块读文件就好了！  但是这样的话，电梯调度模块就能预先知道“将来会发生什么事情”， 例如，调度模块能知道下一分钟有多少人出现在哪些楼层， 她们的目的地是哪里， 调度模块就能预先指挥电梯到相应楼层准备。 这是不符合实际情况的！

测试框架应该处理这个文件， 做必要的信息隐藏，让调度模块只知道当前在系统中的乘客的情况。

挑战5. 如何处理时间的流动？

考虑这个情况：一个乘客A是上午8点钟出现，从1楼到 10楼，  下一个乘客B是上午9点钟出现，从 5 楼到9楼。

如果在告知调度模块乘客A的情况后，马上告知乘客B 的情况， 就会出现时间的错乱，调度模块可以让同一部电梯在五楼停下接乘客B， 但是乘客B是一小时后才按请求电梯的电钮！

很多同学的反应就是把这个测试框架做成一个实时系统， 有一个严格的时钟，各个部件按照时钟运行。 那么， 这个系统要等待一个小时，才告知调度模块乘客B 的信息么？

建议：考虑 “事件驱动的模型”，  在没有任何事件的情况下，时钟就可以向前拨！  注意，有些优秀的调度算法会这样设计：

    当目前这一批乘客都送到目的地后两分钟，如果没有乘客来， 就把电梯排到某个位置。

    或者，在 8 点钟把所有电梯都派到一楼等待。

这个事件驱动的模型要能够支持这样的算法。

挑战 6.  如何处理不同电梯到达不同楼层所带来的特例

假设电梯1 只停靠1层，15 - 25 层， 电梯2 停靠1 - 15 层。  乘客在1层，要上20层。电梯2到了，开了门，乘客要上去么？在现实生活中，乘客一般就上去，到15 层出来，再换乘电梯2.  那么，谁来负责实现这个逻辑呢？

挑战 7. 如何写程序生成大量测试数据

我们的电梯要模拟高峰时刻的人流， 上午 7 - 8 点有一千人上班，大部分是从一楼到各个楼层，同时有一半左右的人从各个楼层去 3 层（食堂）吃饭，还有少部分是在各个楼层来回旅行。 助教要手动准备这些数据，还是可以写一个程序生成各种各样的数据？

挑战8. 如何让这个测试框架和 GUI 界面结合起来，可以实时看到电梯运行的效率？

有了电梯的调度算法和电梯的测试模拟框架, 我们可以从数据层面模拟并测试算法的正确性和效率。 那么现在我们要加上展现的部分 – 用GUI  展现电梯系统从运送所有乘客的过程。 想象一幢大楼全都是透明的,  有许多乘客通过电梯上上下下,  电梯外墙的指示灯 (通常有上/下)  两个标识随着乘客的需求或亮或灭。 

实现:  根据第一次结对项目的电梯测试系统, 和你自己的调度模块 (两个同学各带一个调度模块)，任选一种编程语言实现 GUI. 

老师希望看到这样的情形： 助教写的测试框架可以公开地展示至少两个GUI 界面，框架可以加载至少两个调度算法，例如A和B。 所谓的“加载”， 可以是Windows 上面的 Load DLL 动态链接库， 也可以是通过另外的方式（例如 RESTFul 的接口， Socket,  HTTP 等）实现测试框架和调度程序的绑定。 测试框架载入同样的大楼+电梯配置数据（config files),  载入同样的乘客模拟数据。 同时运行算法A 和 B,  GUI 界面显示乘客+电梯在系统中运行的情况， 并且有专门的状态显示（时间，载客人数，KPI， 等）。 

模拟运行完之后，观众应该能很快地看到哪个算法是快速的。 运用这个系统，我们就可以进行淘汰赛，循环赛等， 决定学生调度算法的名次。 

1. Background - pair programming exercise
We need to design an efficient elevator system to carry people to their destinations in a tall office building.    The following is an example of the configuration about elevators:

The Building has 21 floors, 4 elevators, many passengers use these elevators everyday (passenger weight: average 70kg. max 120kg, min 40g).
Other constant data: Elevator speed, door open/close time, passenger time for going in/out of the elevator. We can make reasonable assumptions about these.
The building has 21 floors, from floor 0, 1, ... to 20. Floor 0 is the underground parking level, floor 1 is the lobby level. Most people come in/out the building via these 2 floors.
Elevator name

Service floor list

Passenger limit

Weight limit

1

All floors

10

800 kg

2

floor 1..10

10

800 kg

3

floor 0,1,2..10

20

1600 kg

4

floor 0,1, 11-20

20

2000 kg

*note: in our test program, the configuration of elevators can be changed,  the scheduler need to read the configuraiton at the initialization time via the API.

2. Requirement to Student pairs
2.1 Each pair of students will design a set of interface and class definition so that an algorithm provider can provide his/her implementation to the “elevator scheduler” class.

2.2 We will discuss the student’s submission in the class,  pick the best design.

2.3 after the API is decided,  we will focus on the design of test framework

2.4  1-2 volunteers will implment a “test framework” app,  and the rest student pairs will each pair will focus on the implementation of the “elevator scheduler” program.

 

consideration for the API:

a) how to keep it simple.

b) how to provide enough info for the scheduler to finish the scheduling work,  without knowing too much info?

c) which component is actually driving the elevator?

d) how to regulate proper passenger behavor?  (e.g. if a passenger needs to go to floor 3 from floor 20, but the current elevator can’t go there directly, what should the passenger do?)

 

consideration for the test framework:

a) how to make sure it generates the same result for the same test cases on a given scheduler?

b) how to check the correctness of the scheduler?

c) how to prevent “cheating” by the scheduler? 

d) how to emulate the “real world” efficiently?  (e.g. if 2 passengers are 30 minutes away, does the test framework need to wait for 30 minutes?)

TA will come up with a consistent testing model to test your program according to the “rush hour” scenario (see below), and record the total travel time of all passengers.

You (student pair) have:

1) A set of API

2) A simple solution (Bus program)

3) A set of test cases to run

 

2.5 Explanation of BUS program:
We can have a worst case algorithm called “bus”. This algorithm treats an elevator as a bus, it goes from bottom to top, stops at every floor, open the door, to let people in and out, then close the door and move on. After it reaches the top floor, it will go down. This algorithm can serve all requests, but it’s apparently not the fastest algorithm.

Your code is required to be managed code (C#, managed C++, etc).

 

It has to generate 0 (zero) Code Analysis warnings and errors. ( link for Code Analysis in Visual Studio)
It has to be correct,  all passengers can reach their destinations
It should be as fast as possible. 
It should not have randomness in scheduling (this is to avoid randomness in testing).
Score guideline: TA will evaluate the “average total travel time” for all passengers in the same test case, the lower, the better. If your performance is lower than “bus” solution, you get 0 points; if your program can’t deliver any passenger to the correct destination, you get 0 points.

 

One hint about elevator scheduling: When total weight is within 40 kg of the max limit, or the number of passengers is already at maximum, the elevator doesn’t need to stop for more external requests.

The elevator scheduler program doesn’t know how many passengers are waiting on each floor, it doesn’t know how many passengers will show up either. This is the same with the real world situation.

3. Testing
TA will simulate a “rush hour” test. The “rush hour” test is to simulate the come-to-work and leave-work scenario in a business building, which has the following 2 parts (they can be run next to each other).

1) Simple test. 20 passengers

20 people going thru random floors within 5 minutes.

 

2) Come-to-work. 1000 total passengers,  duration: 60 minutes



3) Leave-work. 1000 total passengers, duration: 45 minutes




参考文献
注解：这个作业从 2010 年开始，经历 10 年的时间，由北航等学校的老师和同学做了很多遍， 由于学生的项目不是开源的，导致同学们交了作业，做了测试后，源代码就逐渐消失了。
我们收集了部分学生的博客， 从中大家可以了解不同的解题思路，从同学们留下的各种不太完全的文档中，我们大概可以反向工程出来这个项目原来的 Interface 设计和单元测试的接口。 

2010: 
https://www.cnblogs.com/codingcrazy/archive/2010/12/11/1903025.html
1. 引言摘要：本篇博客详细讲述电梯调度算法的流程，测试程序的框架，以及测试文件（XML）的生成。继上一个结对编程项目（3D中国跳棋 —— 记与子禾童鞋的结对编程（附网站地址及完整源码））之后，我们迅
https://www.cnblogs.com/codingcrazy/archive/2010/12/11/1903025.html
2012:

https://www.cnblogs.com/skyjoker/archive/2012/10/24/2737234.html
迟到的总结-By Glede队友连昭鹏的总结：http://www.cnblogs.com/lzplzp/archive/2012/10/22/2732946.html我们一开始交流的时候，就决定基本
https://www.cnblogs.com/skyjoker/archive/2012/10/24/2737234.html

https://www.cnblogs.com/quanfengnan/archive/2012/10/22/2733922.html
第二次作业的结对编程项目：电梯调度系统结对编程小组成员：吴煜10061149 全风楠10061186 这次的作业与个人项目不同，不是从头写一个新的程序，而是在一个已有的程序之上做修改然后实现新的功能。
https://www.cnblogs.com/quanfengnan/archive/2012/10/22/2733922.html

2013: 
https://www.cnblogs.com/RylynnMao/p/3358328.html
结对编程 附加作业毛宇 11061171程志 10061188#1 [附加题]改进电梯调度的interface设计,让它更好地反映现实,更能让学生练习算法,更好地实现信息隐藏和信息共享。其实在学习这个
https://www.cnblogs.com/RylynnMao/p/3358328.html

https://www.cnblogs.com/freestyle-sn/archive/2013/01/09/2852662.html
结对成员：杨鹏飞（193）邓嘉（164）老师给定的电梯调度程序是一个C#命令行程序，其中电梯调度算法是第一次结对编程时我们自己编写的。电梯调度要求的博文地址：http://www.cnblogs.co
https://www.cnblogs.com/freestyle-sn/archive/2013/01/09/2852662.html
      这是一组优秀的博客：

https://www.cnblogs.com/yinpc/archive/2012/10/24/2736462.html
结对编程之各博文传送门经过Yin组长的威逼利诱，我们小组三人终于完成了结对编程项目，本着赚分的基本思想，狂发博文，现将各篇博文地址汇总如下结对编程的感想（殷鹏程，谷骞，陈宇宁）http://www.c
https://www.cnblogs.com/yinpc/archive/2012/10/24/2736462.html

2014:
https://www.cnblogs.com/buaawd/p/4032744.html
结对人员：马佐霖 王迪1.结对编程 1.1结对编程优缺点 （1）首先应该是结对编程的高效率了，结对编程的时候，两个人可以分开做不同的unit，也可以同时做相同的unit。在项目的一些简单的unit，一
https://www.cnblogs.com/buaawd/p/4032744.html
https://www.cnblogs.com/hks1994/p/4034028.html
本次项目进行结对编程的训练。项目要求http://www.cnblogs.com/jiel/p/3997895.html#3045439结对编程人员：12061228晏旭瑞、12061203黄可嵩一.
https://www.cnblogs.com/hks1994/p/4034028.html

2015:
https://www.cnblogs.com/mtj3344/p/4819628.html
电梯调度结对编程 1.题目：设计一个电梯调度算法，实现基本的电梯调度功能，要求有四部电梯，每部电梯21层，并且具有重量检验算法。2.设计前的准备：确定了结对之后，我们首先对设计中可能遇到的问题进行了大
https://www.cnblogs.com/mtj3344/p/4819628.html
      这个项目有源代码： Github：https://github.com/mtj075/Elevator.git 

2016： 
      JavaScript 的实现：

https://www.cnblogs.com/libaoquan/p/5326683.html
写在前面 我和我的小伙伴 结队成员：李宝全 & 黄一凡 黄一凡的博客首页：http://www.cnblogs.com/huangyifan/ cooding链接：https://coding
https://www.cnblogs.com/libaoquan/p/5326683.html
https://www.cnblogs.com/mohaozhong/p/5369209.html
电梯调度项目： 项目分析与需求： 从题目上来看，项目要求编写一个掌控电梯的程序。电梯这个东西，大家都乘过，无非就是：乘客上电梯，判断是否超重，乘客选择想要达到的楼层，最后依次去到离需求最近的一个楼层。
https://www.cnblogs.com/mohaozhong/p/5369209.html

2021:
https://blog.csdn.net/qq_42714429/article/details/113742774
结对项目：电梯调度本博客用以记述完成整个软件工程基础大作业项目的完成过程。项目完成人：Zhang Junrui，Feng Maike一、准备阶段时间预估表：PSP2.1Personal Software Process Stages预估耗时（分钟）实际耗时（分钟）Planning计划6030· Estimate· 估计这个任务需要多少时间6030Development开发11001330· Analysis· 需求分析 (包括学习新技术
https://blog.csdn.net/qq_42714429/article/details/113742774

2022:
https://blog.csdn.net/qq_42714429/article/details/113742774
结对项目：电梯调度本博客用以记述完成整个软件工程基础大作业项目的完成过程。项目完成人：Zhang Junrui，Feng Maike一、准备阶段时间预估表：PSP2.1Personal Software Process Stages预估耗时（分钟）实际耗时（分钟）Planning计划6030· Estimate· 估计这个任务需要多少时间6030Development开发11001330· Analysis· 需求分析 (包括学习新技术
https://blog.csdn.net/qq_42714429/article/details/113742774


​
