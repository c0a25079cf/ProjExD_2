import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:(0, -5),
    pg.K_DOWN:(0, 5),
    pg.K_LEFT:(-5, 0),
    pg.K_RIGHT:(5, 0)
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rect: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectか爆弾Rect
    戻り値：タプル（横方向判定結果、縦方向判定結果）
    画面内ならTrue、画面外ならFalse
    """
    yoko, tate = True, True
    if rect.left < 0 or WIDTH < rect.right:  # 横方向判定
        yoko = False
    if rect.top < 0 or HEIGHT < rect.bottom:  # 縦方向判定
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    引数：画面Surface
    戻り値：なし
    5秒間ゲームオーバー画面を表示する
    """
    GOscreen = pg.Surface((WIDTH, HEIGHT))  # 空のSurface
    pg.draw.rect(GOscreen, (0, 0, 0), pg.Rect(0, 0, WIDTH, HEIGHT))  # 黒い四角形
    GOscreen.set_alpha(180)  # 透明度の設定
    GO_rct = GOscreen.get_rect()
    screen.blit(GOscreen, [0, 0])
    fonto = pg.font.Font(None, 80)
    txt = fonto.render("Game Over", True, (255, 255, 255))  # 白のGameOverの文字
    txt_rct = txt.get_rect()
    txt_rct.center = GO_rct.center
    screen.blit(txt, txt_rct)
    ck_img1 = pg.image.load("fig/8.png")
    screen.blit(ck_img1, [300, 300])
    screen.blit(ck_img1, [750, 300])
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    引数：なし
    戻り値：タプル（大きさを変えた爆弾Surfaceのリスト、加速度のリスト）
    """
    bb_imgs = []
    for r in range(1, 11):  # 10段階の爆弾Surfaceを生成、リスト化
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0))
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]  # 10段階の加速度リスト
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    kk_img = pg.image.load("fig/3.png")
    kk_img_flip = pg.transform.flip(kk_img, True, False)
    kk_dict = {
        ( 0, 0): pg.transform.rotozoom(kk_img, 0, 1.0),  # キー押下が無い場合
        (+5, 0): pg.transform.rotozoom(kk_img_flip, 0, 1.0),  # 右
        (+5,-5): pg.transform.rotozoom(kk_img_flip, -45, 1.0),  # 右上
        ( 0,-5): pg.transform.rotozoom(kk_img_flip, -90, 1.0),  # 上
        (-5,-5): pg.transform.rotozoom(kk_img, -45, 1.0),  # 左上
        (-5, 0): pg.transform.rotozoom(kk_img, 0, 1.0),  # 左
        (-5,+5): pg.transform.rotozoom(kk_img, 45, 1.0),  # 左下
        ( 0,+5): pg.transform.rotozoom(kk_img_flip, 90, 1.0),  # 下
        (+5,+5): pg.transform.rotozoom(kk_img, 45, 1.0)  # 右下
    }
    return kk_dict


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    bb_img = pg.Surface((20, 20))  # 空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 半径10の赤い円
    bb_img.set_colorkey((0, 0, 0))  # 余りの黒を透過
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_rct = bb_img.get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 練習2：爆弾初期速度
    clock = pg.time.Clock()
    tmr = 0
    bb_imgs, bb_accs = init_bb_imgs()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        if kk_rct.colliderect(bb_rct):  # kkとbbのrectが重なっていたら
            print("game over")
            gameover(screen)
            return

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += -5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += -5
        for k, tpl in DELTA.items():
            if key_lst[k]:
                sum_mv[0] += tpl[0]  # 横方向移動量
                sum_mv[1] += tpl[1]  # 縦方向移動量
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):  # 画面外へのはみだし
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 動きのキャンセル
        screen.blit(kk_img, kk_rct)
        avx = vx*bb_accs[min(tmr//500, 9)]
        avy = vy*bb_accs[min(tmr//500, 9)]
        bb_img = bb_imgs[min(tmr//500, 9)]
        if not bb_rct == bb_img.get_rect():
            bb_rct.width = bb_img.get_rect().width
            bb_rct.height = bb_img.get_rect().height
        bb_rct.move_ip(avx, avy)  # 練習2：爆弾移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # yoko == False
            vx *= -1  # 動きの反転
        if not tate:  # tate == False
            vy *= -1  # 動きの反転
        screen.blit(bb_img, bb_rct)  # 練習2：爆弾表示
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
