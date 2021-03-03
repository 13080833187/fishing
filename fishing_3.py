import pgzrun
import random
import math
import copy
import time
import shelve
from pgzero.builtins import Actor, animate, keyboard

class FISH:
    def __init__(self, name, speed, price, EXPProvided, rarity, interval):
        self.name = name
        self.speed = speed#包含4个数字的元组，s[0]表示最大下降加速度<0，s[3]表示最大上升加速度
        self.price = price#鱼的售价，分为四个星级(各星级之间有固定比例）
        self.pos = FISHING_BOTTOM - 15#当前鱼的位置
        self.interval = interval
        #self.curSpeed
        #self.holdtime
        self.stop = False
        self.EXPProvided = EXPProvided#钓上来以后提供的经验值
        self.rarity = rarity#按照稀有度分成若干级，不同钓鱼等级钓上来的比例不同
        self.perfectCaught = True

    def move(self, player):#决定了鱼在钓鱼槽中的运动情况
        SP = player.rod.special
        if not self.holdtime:
            self.holdtime = random.randint(self.interval[0], self.interval[1])
            if self.stop:
                self.curSpeed = random.choice([random.uniform(self.speed[0], self.speed[1]),
                                               random.uniform(self.speed[2], self.speed[3])])#鱼当前的速度
            else:
                self.curSpeed = random.uniform(self.speed[0] / 10, self.speed[3] / 10)
            self.stop = not self.stop
        v = self.curSpeed
        self.pos -= v#上升y值减小
        if self.pos < FISHING_TOP:
            self.pos = (FISHING_TOP * 2 )- self.pos
            self.curSpeed = 0
        elif self.pos > FISHING_BOTTOM - 15:
            self.pos = (FISHING_BOTTOM * 2) - self.pos - 30
            self.curSpeed = 0
        self.holdtime -= 1
       
    def Caught(self, player):#后续还可以添加图鉴记录（是否钓到了什么鱼，钓到的鱼的最大最小长度）
        global FUNC_LIST, star_list
        self.star = player.cal_star() + int(self.perfectCaught)
        if self.price:
            star_list[self.star - 1] += 1
        SP = player.rod.special
        if SP:
            if SP ==  'The quality of fish is rising' and random.randint(1, 2) > 1:
                self.star = min(3, self.star + 1)
        player.gold += int(self.price * (1 + (self.star * 0.25) + ((self.star == 3) * 0.25)))
        player.experience += self.EXPProvided
        player.upgrade()#检测是否升级
        FUNC_LIST[self.printCaught] = 150
        sounds.success.play()
        countFish(self.name) 
        global CHEST_LIST, chestConfirm
        if player.cur_Chest and player.cur_Chest.haveCaught:
            if player.cur_Chest.type:
                chestConfirm = False
                CHEST_LIST.append(player.cur_Chest.printCaught)
            else:
                chestConfirm = True
        
    def printCaught(self):#钓到鱼后，左下角打印出钓到了什么鱼
        screen.blit('fish_bg_80', (200, 245))
        if '_' in self.name:
            tmp = self.name.split('_')
            screen.draw.text(tmp[0].upper(), (245, 340),
                         fontsize = 12, color=(77, 109, 213 ))
            screen.draw.text(tmp[1].upper(), (245, 350),
                         fontsize = 12, color=(77, 109, 213 ))           
        else:
            screen.draw.text(self.name.upper().replace('_', ' '), (245, 345),
                         fontsize = 16, color=(77, 109, 213 ))
        screen.blit(self.name, (250, 295))
        screen.draw.text("EXP +" + str(self.EXPProvided), (245, 360), fontsize= 20, color=(41, 77, 198))
        if self.price:
            if self.star == 1:
                screen.blit('24px-silver_quality_icon',(290, 320))
            elif self.star == 2:
                screen.blit('24px-gold_quality_icon', (290, 320))
            elif self.star == 3:
                screen.blit('24px-iridium_quality_icon', (290, 320))

    def printFail(self):
        screen.draw.text("Fail", (482, 150), fontsize=30, color=(255, 80, 49))
         
        
class ROD:
    def __init__(self, level, special):#钓竿最基础是1级！！
        self.level = int(level)#钓鱼等级
        self.special = str(special)#特殊情况，可以先不管，好像很复杂(str）
        self.barSpeed = 1.2#进度条上升的速度（也可以写在其他位置QAQ）
        self.clickSpeed = 1.0
        self.escapeSpeed = 0.8
        self.gravity = 0.6


class Chest:
    def __init__(self, r, pos):#type表示宝箱类型：0为空，1为有鱼饵，2为有鱼竿
        global player
        self.pos = pos
        if 1 <= r <= 3:
            self.bait = random.randint(10, 50)
            self.type = 1
        elif 4 <= r <= 5:
            self.rod= randomRod(player.rod.level + 1, True)
            self.type = 2
        else:
            self.type = 0
        self.progressBar = 0  #宝箱进度条(总共24px)
        self.barSpeed = 0.3  #宝箱进度条上升速度
        self.haveCaught = False
        
    def Caught(self, player):
        if 1 <= random <=3:
            player.bait += self.bait
        
    def getSpeed(self):
        return self.barSpeed
       
    def printChest(self):#在钓鱼槽中打印出chest(24px),其上方打印出进度条(也是24px宽，有变色)
        screen.blit('24px-chest', (392, self.pos))
        screen.blit('chest_process', (370, self.pos - 30))
        p = self.progressBar
        c = (255 if p < 12 else int(255 * (24 - p) / 12), (p / 12) * 255 if p < 12 else 255, 0)
        screen.draw.filled_rect(Rect((376, self.pos + 40 - p / 24 * 70), (4, (p / 24) * 70)), c)
       
       
    def printCaught(self):#如果最终钓鱼成功，则打印出界面
        if self.type == 1:
            screen.blit('a_70', (0, 0))
            screen.blit('shop_bait', (380, 120))
            screen.draw.text("×" + str(self.bait), (580, 220), fontsize=42, color=(0, 0, 0))
            CONFIRM.draw()
        if self.type == 2:
            screen.blit('a_70', (0, 0))
            screen.blit('shop_rod', (380, 120))
            r = len(self.rod.special) // 2
            for i in range(r, len(self.rod.special)):
                if self.rod.special[i] == ' ':
                    r = i
                    break
            screen.draw.text(self.rod.special[:r], (580, 220), fontsize=30, color=(0, 0, 0))
            screen.draw.text(self.rod.special[r+1:], (580, 250), fontsize=30, color=(0, 0, 0))            
            CONFIRM.draw()


class PLAYER:
    def __init__(self, rod, gold, experience, level, bait):#人物最初是1级！！
        self.rod = rod
        self.gold = gold
        self.experience = experience
        self.level = level
        self.bait = bait
        self.FISHING = False #是否正在钓鱼
        self.progressBar = FISHING_BOTTOM#进度条底部Y值
        self.mouseFlag = False
        self.fishbarPos = FISHING_BOTTOM#钓鱼条底端的位置（y值较大）
        self.cur_Barspeed = 0
        self.cur_Chest = None
        self.inShop = False#是否正在商店中
        self.inCollection = False
        
    def coverFish(self):#当前钓鱼条覆盖了?
        global cur_fish
        topPos = - player.calLen() + self.fishbarPos#计算钓鱼条上端位置
        if  self.fishbarPos >= cur_fish.pos >= topPos:
            return True
        return False
    
    def upgrade(self):
        while self.experience >= self.level ** 2:
            self.level += 1
            FUNC_LIST[self.printUpgrade] = 150
    
    def printUpgrade(self):
        screen.draw.text('Level Up!', (30, 270), fontsize = 30, color = (255, 246, 73))
    
    def getWaitTime(self):
        l = self.level + self.rod.level
        tmp = math.log(l,2)
        w = [10 / tmp, 20 / tmp]
        if self.bait:
            self.bait -= 1
            return [x * 0.9 for x in w]
        return w
    
    def cal_star(self):#返回鱼的品质
        l = self.level + self.rod.level
        tmp = random.uniform(0,1)
        if 0 <= tmp <= math.log(math.e, l):
            return 0
        elif 1 - min(0.5, max(math.log(l/8, 8),0)) <= tmp <= 1:
            return 2
        return 1        
    
    def getRarity(self):#返回鱼的稀有度
        l = self.level + self.rod.level
        r = []
        for i in range(5):
            r.append(rarity_proportion[min(39 - i,max(l - i - 1, 0))])
        s = sum(r)
        ans = random.randint(1, s)
        for i in range(5):
            if r[i] >= ans:
                return i
            ans -= r[i]            
    
    def printInfo(self):#打印出当前玩家的金钱，钓鱼级别和鱼饵数
        screen.blit('player', (0, 10)) # 显示玩家信息的背景图
        screen.blit('levelup', (10, 190)) # 显示升级信息的背景图
        # 升级信息图上的经验条，经验条总长度为86
        screen.draw.filled_rect(Rect((77, 232), (86 * self.experience / self.level ** 2, 11)), (158, 161, 247))
        screen.draw.text(str(self.experience) + " / " + str(self.level ** 2), (89, 230), fontsize=25, color=(255, 250, 118))
        screen.draw.text("GOLD: " + str(self.gold), (40, 100), fontsize=30, color=(231, 250, 255))
        screen.draw.text("LEVEL: " + str(self.level), (40, 125), fontsize=30, color=(231, 250, 255))
        screen.draw.text("BAIT: " + str(self.bait), (40, 150), fontsize=30, color=(231, 250, 255))
    
    def escapeSpeed(self):#进度条下降
        return self.rod.escapeSpeed
        
    def calLen(self):#返回长度：正值
        return (min((self.level + self.rod.level) * 3, 120) + 60) * (1 + ((self.rod.special == 'Increase the length of fishing bar') * 0.2))
        
    def getSpeed(self):#返回向上速度时是正值
        if self.mouseFlag:
            self.cur_Barspeed += self.rod.clickSpeed
        elif abs(self.fishbarPos - FISHING_BOTTOM) < 1e-6:#钓鱼条停在池底
            self.cur_Barspeed *= -0.4
        else:
            self.cur_Barspeed -= self.rod.gravity + (0.2 * ( self.rod.special == 'Increase weight of fishing rod'))
        return self.cur_Barspeed
    
    def barSpeed(self):#进度条上升
        return self.rod.barSpeed
    
    def findChest(self):
        if self.rod.special == 'Chest is more likely to appear':
            r = random.randint(1, 1)
        else:
            r = random.randint(1, 1)
        if r == 1:
            self.cur_Chest = randomChest(self)
            return True
        return False
    
    def coverChest(self):#当前钓鱼条覆盖了?
        topPos = - self.calLen() + self.fishbarPos#计算钓鱼条上端位置
        if  self.fishbarPos >= self.cur_Chest.pos >= topPos - 15:
            return True
        return False
    
def randomRod(level, isChest = False, special = None):#isChest表示是否是宝箱生成的随机钓竿
    if isChest:
        special = random.choice(SPECIAL_LIST)
    return ROD(level, special)

def randomChest(player_):
    if player_.rod.special == 'The probability of empty chest decreases':
        r = random.randint(1,8)
    else:
        randnum = random.randint(1,10)
    place = random.uniform(FISHING_TOP + 70, FISHING_BOTTOM - 70)
    return Chest(randnum, place)

WIDTH = 960
HEIGHT = 540
FISHING_BOTTOM = 460
FISHING_TOP = 65

#读取存档（如果有的话
FILE = shelve.open('data')
if FILE:
    player = PLAYER(ROD(FILE['rod']['level'], FILE['rod']['special']),
                    FILE['gold'], FILE['experience'], FILE['level'], FILE['bait'])
    collect_list = FILE['collect']
    star_list = FILE['star']

else:
    player = PLAYER(randomRod(1), 0, 0, 1, 0)
    collect_list = [[0] * 6, [0] * 9, [0] * 10,  [0] * 7, [0] * 9]
    star_list = [0] * 3
FILE.close()
player.inShop = False
player.inCollection = False
player.FISHING = False
FUNC_LIST = {}
CHEST_LIST = []
chestConfirm = True
waitTimeClock = 0

#不同等级时钓到鱼的稀有度使用准备好的fib数列
rarity_proportion = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181,
                     6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040,
                     1346269, 2178309, 3524578, 5702887, 9227465, 14930352, 24157817, 39088169, 63245986]

TOTALFISH = [[FISH('trash', (0, 0, 0, 0), 0, 0, 0, (1,1000)),
              FISH('driftwood', (0, 0, 0, 0), 0, 0, 0, (1,1000)),
              FISH('soggy_newspaper',  (0, 0, 0, 0), 0, 0, 0, (1,1000)),
              FISH('broken_cd',  (0, 0, 0, 0), 0, 0, 0, (1,1000)),
              FISH('seaweed',  (0, 0, 0, 0), 0, 0, 0, (1,1000)),
              FISH('carp', (0, 0, 0, 0.5), 15, 1, 1, (10, 20)),
              FISH('carp', (0, 0, 0, 0.5), 15, 1, 1, (10, 20)),
              FISH('carp', (0, 0, 0, 0.5), 15, 1, 1, (10, 20)),
              FISH('carp', (0, 0, 0, 0.5), 15, 1, 1, (10, 20)),
    ],[FISH('chub', (-2, -0.5, 2, 4.5), 50, 2, 1, (20, 40)),
       FISH('anchovy', (-2, -1, 2, 4), 45, 2, 1, (20, 35)),
       FISH('sardine',(-2, -1.5, 3, 5), 60, 3, 1, (15, 30)),
       FISH('bream',(-3, 0, 0, 5), 67, 3, 1, (10, 25)),
       FISH('smallmouth_bass',(-5,0, 0, 5), 50, 2, 1, (15, 35)),
       FISH('perch',(-3, 0, 1, 4), 55, 3, 1, (25, 30)),
       FISH('sunfish',(-2, 0, 0, 2), 25, 2, 1, (30, 45)),
       FISH('herring',(-1, 0, 0, 1), 30, 1, 1, (30, 45)),
       FISH('red_snapper',(-3,0, 0, 6), 50, 3, 1, (15, 30))
        ],[FISH('largemouth_bass', (-5, 0, 0, 7), 100, 6, 2, (15, 20)),
           FISH('rainbow_trout',(-5, 0, 0, 5), 65, 5, 2, (20, 25)),
           FISH('salmon',(-6, 0, 0, 6), 75, 6, 2, (20, 30)),
           FISH('walleye',(-7,0, 0, 8), 105, 6, 2, (20, 30)),
           FISH('pike',(-8, -2, 3, 6), 100, 8, 2, (5, 15)),
           FISH('red_mullet',(-6, 0, 0, 6), 75, 8, 2, (15, 25)),
           FISH('flounder',(-9, 0, 0, 4), 100, 7, 2, (30, 45)),
           FISH('tilapia',(-5, 0, 0, 6), 75, 6, 2, (20,40)),
           FISH('shad',(-4, 0, 0, 6), 60, 5, 2, (15, 40)),
           FISH('bullhead',(-3, 0, 0, 5), 60, 6, 2, (20, 30)),
            ],[FISH('tuna',(-9, 0, 0, 11), 150, 13, 3, (10, 18)),
               FISH('catfish',(-8, -1, 3, 12), 200,16, 3, (5, 20)),
               FISH('eel',(-10, -2, 2, 10), 85, 14, 3, (5, 14)),
               FISH('tiger_trout',(-9, 0, 0, 12), 150, 15, 3, (12, 20)),
               FISH('dorado',(-8, 0, 0, 8), 100, 12, 3, (20, 30)),
               FISH('albacore',(-7, 0, 0, 7), 75, 10, 3, (10, 20)),
               FISH('halibut',(-6, 0, 0, 7), 80, 11, 3, (8, 20))
                ],[FISH('pufferfish',(-18, -6, 5, 25), 200, 20, 4, (5, 10)),
                   FISH('octopus',(-30, -20, 20, 40), 350, 25, 4, (5, 10)),
                   FISH('sea_cucumber',(-20, -10, 15, 24), 250, 24, 4, (10, 15)), 
                   FISH('squid',(-20, -8, 12, 20), 200, 20, 4, (10, 20)),
                   FISH('sturgeon',(-15, -8, 10, 20), 200, 25, 4, (5, 10)),
                   FISH('lingcod',(-20, 0, 0, 20), 120, 24, 4, (8, 12)),
                   FISH('angler',(-20, 0, 0, 25), 400, 40, 4, (5, 15)),
                   FISH('crimsonfish',(-30, -15, 15, 30), 400, 40, 4, (5, 8)),
                   FISH('legend',(-35, -20, 15, 30), 600, 55, 4, (5, 8))
                    ]]#包含了所有鱼的列表，按不同稀有度分级：垃圾——（鲤鱼）——（比目鱼）——(金枪鱼）——（章鱼）——（传说鱼？）
SPECIAL_LIST = ['Chest is more likely to appear',
                'The probability of empty Chest decreases',
                'Progress bar drops more slowly',
                'Increase the length of fishing bar',
                'Shorter waiting time for fish to bite',
                'The goods in the shop are cheaper',
                'Increase weight of fishing rod',
                'The speed of fish is more stable',
                'The fishing rod doesn\'t bounce back',
                'The initial speed of the fish is reduced',
                'The quality of fish is rising',
                'There are more rare fish'
                ]

#按键部分：打印出边框和底色，其中写出按键名（英文大写）
BUY_BAIT = Actor('shop_buy', center = (320, 380))
ROD_LEVELUP = Actor('shop_levelup', center = (580, 390))
SHOP = Actor('shop_shop', center = (870, 40))
SAVE = Actor('shop_save', center = (870, 95))
COLLECTION = Actor('shop_course', center = (870, 150))#to do
EXIT = Actor('shop_exit', center = (870, 205))
music.set_volume(0.3)
music.play('backgroundmusic')
CONFIRM = Actor('ok', center = (480, 360))

TITLE = 'FISHING'

def countFish(name):
    global collect_list
    tmp = [6,9,10,7,9]
    for i in range(5):
        for j in range(tmp[i]):
            if TOTALFISH[i][j].name == name:
                collect_list[i][j] += 1
                return


def printFishing():#打印包含钓鱼窗口，钓鱼槽，进度条和鱼的位置，钓鱼条位置(new : draw Chest!!!)
    screen.blit('process', (320, 50))
    htmp = player.calLen() # 钓鱼条长度
    screen.draw.filled_rect(Rect((393, player.fishbarPos - htmp), (22, htmp)), (52, 255, 72)) # 钓鱼条
    if cur_fish.price < 400:
        screen.blit('24px-anchovy', (392, cur_fish.pos)) # 钓鱼条上的鱼
    else:
        screen.blit('24px-spook_fish', (392, cur_fish.pos)) # 钓鱼条上的鱼
    process = (480 - player.progressBar) / 410 # 进度（0-1之间浮点数）
    color = (255, 255, 55)
    if process < 0.5:
        color = (255, int(55 + 400 * process), 55)
    else:
        color = (int(255 - 400 * (process - 0.5)), 255, 55)
    screen.draw.filled_rect(Rect((435, player.progressBar), (5, 460 - player.progressBar)), color) # 画进度条
    if player.cur_Chest and not player.cur_Chest.haveCaught:
        player.cur_Chest.printChest()


def printCollection():#打印图鉴
    screen.blit('a_70', (0, 0))
    screen.blit('shop', (10, 0))
    placex = 150
    placey = 80
    tmp = [6,9,10,7,9]
    for i in range(5):
        for j in range(tmp[i]):
            if collect_list[i][j] and TOTALFISH[i][j].price:
                screen.blit('24px-'+TOTALFISH[i][j].name, (placex, placey))                
                screen.draw.text(f"%s: %d"%(TOTALFISH[i][j].name.upper().replace('_', ' '),collect_list[i][j]),
                                 (placex +30, placey), fontsize = 24, color = (255, 255, 0))
                placey += 30
            elif TOTALFISH[i][j].price:
                screen.draw.text("???:0", (placex +30, placey), fontsize = 24, color = (255, 255, 0))
                placey += 30
            if placey > 450:
                placex += 220
                placey = 80
    STAR = ['24px-silver_quality_icon','24px-gold_quality_icon','24px-iridium_quality_icon']
    for i in range(3):
        screen.blit(STAR[i], (placex + 15, placey - 15))                
        screen.draw.text(':%d'%(star_list[i]),
                                 (placex +30, placey), fontsize = 24, color = (255, 255, 0))
        placey += 30

def printFailedBuy():
    screen.draw.text("You don't have enough money", (110, 210), fontsize = 72, color = (255, 99, 71))

def printSuccessBuy():
    screen.draw.text("Successfully buy it", (215, 210), fontsize = 72, color = (192, 255, 62))

def printSave():
    screen.draw.text("Game saved", (265, 210), fontsize = 72, color = (255, 236, 139))

def printShop():#打印出购买鱼饵和升级钓竿，分成两部分，图片最好要有边框
    screen.blit('a_70', (0, 0))
    screen.blit('shop', (10, 0))
    screen.blit('shop_bait', (220, 115))
    screen.blit('shop_rod', (480, 115))
    r = (player.rod.special == 'The goods in the shop are cheaper')
    discount = 1 - (r * 0.1)
    screen.draw.text('PRICE: ' + str(int(50 * discount)), (260, 310), fontsize = 36, color = (255, 255, 0))
    screen.draw.text('PRICE: ' + str(int((player.rod.level + 1) * 50 * discount)), (520, 310), fontsize = 36, color = (255, 255, 0))
    BUY_BAIT.draw()
    ROD_LEVELUP.draw()

def printMenu():#右下角打印出SHOP, SAVE, Collection, EXIT
    SHOP.draw()
    SAVE.draw()
    COLLECTION.draw()
    EXIT.draw()

def startFishing():#根据当前等级和鱼竿随机出等待时间和上钩的鱼（或垃圾）
    global player
    global CHEST_LIST
    CHEST_LIST = []
    SP = player.rod.special
    #waitTime = player.getWaitTime()#list
    #wait = random.uniform(waitTime[0], waitTime[1])
    rarity = player.getRarity()
    if SP ==  'There are more rare fish' and random.randint(1, 10) > 9:
        rarity = min(rarity + 1, 4)
    global cur_fish
    cur_fish = copy.copy(random.choice(TOTALFISH[rarity]))
    cur_fish.curSpeed =  cur_fish.speed[3]#鱼当前的速度
    cur_fish.holdtime = cur_fish.interval[1]
    player.progressBar = FISHING_BOTTOM - 130
    player.FISHING = True
    player.mouseFlag = False
    player.cur_Chest = None
    player.cur_Barspeed = 0
    player.fishbarPos = FISHING_BOTTOM  # 底端的位置（y值较大）
    if SP ==  'The initial speed of the fish is reduced':
            cur_fish.curSpeed *= 0.8
    #time.sleep(wait)
    sounds.success.play()
    time.sleep(1)
    global waitTimeClock
    if cur_fish.price == 0:
        cur_fish.Caught(player)
        waitTimeClock = 0
        player.FISHING = False
        return
    music.play('fishing')

def toFunc():
    global FUNC_LIST, CHEST_LIST, chestConfirm    
    if CHEST_LIST and not chestConfirm:
        CHEST_LIST[0]()
    else:
        for i in FUNC_LIST.keys():
            if FUNC_LIST[i]:
                FUNC_LIST[i] -= 1
                i()

def draw():
    screen.clear()
    screen.blit('background', (0,0))
    screen.blit('fisherman', (370, 160))
    global waitTimeClock
    if not player.FISHING:
        if not waitTimeClock:
            screen.draw.text("Press [SPACE] to start fishing", (300, 480), fontsize=32, color=(255, 255,255))
        elif waitTimeClock > 0:
            screen.draw.text("Waiting fish to bite the hook...", (300, 480), fontsize=32, color=(255, 255,255))
            waitTimeClock -= 1
            if waitTimeClock < 0:
                waitTimeClock = -1
                
                clock.schedule(startFishing, 0.2)
    #screen.draw.rect(Rect((480, 190), (40, 80)), (255, 255, 255))
    screen.draw.text(f'ROD LEVEL:%d'%(player.rod.level), (650, 420), fontsize = 32, color = (255, 255, 255))
    if player.rod.special:
        screen.draw.text("SPECIAL:", (650, 440), fontsize = 32, color = (239, 242, 132))
        screen.draw.text(player.rod.special, (650, 460), fontsize = 18, color = (255, 255, 255))

    player.printInfo()       
    if player.FISHING:
        printFishing()
    else:#正常界面的时候要提示按空格进入钓鱼
        printMenu()
        if player.inShop:
            printShop()
        elif player.inCollection:#正常界面
            toFunc()
            printCollection()
            return
    toFunc()


def update():
    global player
    global cur_fish
    global FUNC_LIST
    global waitTimeClock
    if player.FISHING:#更新一下进度条情况，判定现在钓鱼条是否覆盖了鱼，最后更新鱼的位置，钓鱼条位置在mouse_down中更新
        SP = player.rod.special
        if not player.cur_Chest:
            player.findChest()
        l = player.calLen()
        v = player.getSpeed()#返回向上的速度是正值
        player.fishbarPos -= v
        r = (SP ==  'The fishing rod doesn\'t bounce back')
        if player.fishbarPos > FISHING_BOTTOM:
            if r:
                player.fishbarPos = FISHING_BOTTOM
                player.cur_Barspeed = 0
            else:
                player.fishbarPos = (2 * FISHING_BOTTOM) - player.fishbarPos 
                player.cur_Barspeed *= -0.4
        elif player.fishbarPos - l < FISHING_TOP:
                player.fishbarPos = FISHING_TOP + l
                player.cur_Barspeed = 0
        if player.coverFish():
            player.progressBar -= player.barSpeed()#覆盖的话进度条上升
            if player.progressBar <= FISHING_TOP:
                cur_fish.Caught(player)
                waitTimeClock = 0
                player.FISHING = False
                music.stop()
                music.play('backgroundmusic')
                return
        else:
            player.progressBar += player.barSpeed() * (1 - (0.1 * (SP == 'Progress bar drops more slowly')))
            cur_fish.perfectCaught = False#进度条下降
            if player.progressBar >= FISHING_BOTTOM :#进度条过低(低于FISHING_BOTTOM一定值）
                player.FISHING = False
                music.stop()
                waitTimeClock = 0
                FUNC_LIST[cur_fish.printFail] = 150
                sounds.fail.play()
                music.play('backgroundmusic')
                return

        cur_fish.move(player)
        if player.cur_Chest:
            if player.coverChest():
                player.cur_Chest.progressBar += player.cur_Chest.getSpeed()#覆盖的话进度条上升
                if player.cur_Chest.progressBar >= 24:
                    player.cur_Chest.haveCaught = True
            else:
                player.cur_Chest.progressBar -= player.cur_Chest.getSpeed()
                if player.cur_Chest.progressBar <= 0  :#进度条过低(低于CHEST_BOTTOM一定值）
                    player.cur_Chest.progressBar = 0
    else:
        pass
  
def saveData():
    FILE = shelve.open('data', flag = 'w', writeback = True)
    FILE['rod'] = {'level' : player.rod.level, 'special' : player.rod.special}
    FILE['gold'] = player.gold
    FILE['experience'] = player.experience
    FILE['level'] = player.level
    FILE['bait'] = player.bait
    FILE['collect'] = collect_list
    FILE['star'] = star_list
    FILE.close()
        
def on_mouse_down(pos):
    global player
    global chestConfirm
    global CHEST_LIST
    global FUNC_LIST
    if player.FISHING:#钓竿上移
        player.mouseFlag = True
        return
    else:
        judge = player.inShop or player.inCollection#not judge means in main menu(if not in chestpage)
        if not chestConfirm:
            if CONFIRM.collidepoint(pos):
                chestConfirm = True
                CHEST_LIST = []
                if player.cur_Chest.type == 1:
                    player.bait + player.cur_Chest.bait
                elif player.cur_Chest.type == 2:
                    player.rod = player.cur_Chest.rod
            return
        if SHOP.collidepoint(pos) and not player.inCollection:
            if not judge:#如果原来在主界面
                for i in FUNC_LIST.keys():
                    if i != printFailedBuy and i!= printSuccessBuy:
                        FUNC_LIST[i] = 0
            sounds.confirm.play()
            player.inShop = not player.inShop
            return
        if player.inShop:
            r = (player.rod.special == 'The goods in the shop are cheaper')
            discount = 1 - (r * 0.1)
            if BUY_BAIT.collidepoint(pos):
                if player.gold >= 50 * discount:
                    player.gold -= int(50 * discount)
                    player.bait += 10
                    FUNC_LIST[printSuccessBuy] = 60
                    sounds.confirm.play()
                else:
                    FUNC_LIST[printFailedBuy] = 60
                    sounds.warn.play()
            if ROD_LEVELUP.collidepoint(pos):
                price = int((player.rod.level + 1) * 50 * discount)
                if player.gold >= price:
                    player.gold -= price
                    player.rod = randomRod(player.rod.level + 1, special = player.rod.special)
                    FUNC_LIST[printSuccessBuy] =60
                    sounds.confirm.play()
                else:
                    FUNC_LIST[printFailedBuy] = 60
                    sounds.warn.play()
            return
        if SAVE.collidepoint(pos) and not judge:
            sounds.confirm.play()
            saveData()
            FUNC_LIST[printSave] = 60
        elif COLLECTION.collidepoint(pos) and not player.inShop:
            sounds.confirm.play()
            player.inCollection = not player.inCollection
        elif EXIT.collidepoint(pos) and not judge:
            sounds.confirm.play()
            saveData()
            exit()


def on_mouse_up():
    global player
    if player.FISHING:
        player.mouseFlag = False


def on_key_down(key):
    global player, waitTimeClock
    if not player.FISHING and waitTimeClock <= 0:
        if key == keys.SPACE:
                waitTime = player.getWaitTime()#list
                wait = random.uniform(waitTime[0], waitTime[1])
                if player.rod.special == 'Shorter waiting time for fish to bite':
                    wait *= 0.9
                waitTimeClock = (wait * 60) - 12
        

pgzrun.go()
