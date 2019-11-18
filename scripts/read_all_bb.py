import sys
import random
from collections import namedtuple
from pathlib import Path
import openslide
import cv2
import pandas as pd
import shutil


"""
<Description>
Read single ndpi file and bb data, converting to output_width
output_height img with the other bb data.

<USAGE>
    python read_all_bb.py <single_original_ndpi>\
                          <cropped_images_dir>\
                          <output_width>\
                          <output_height>\
                          <prefix>\
                          <output_dir>

<cropped images dir>
here
├── benign
├── intermediate
└── malignant

<prefix>
Any strings to add at the head of new image file.

ex: prefix="AAA" & cropped png name="BBB.png"
    => new png name="AAABBB.png"


<annotations>
Annotations file contains the params below.
{clsnum[line.cls]}
{centerx_line / newwidth}
{centery_line / newheight}
{width_line / newwidth}
{height_line / newheight}

"""


def run():
    img, img_paths, clsnum, dir_check, o_width, o_height, prefix, output_dir = beforehand()
    make_output_dir(dir_check, output_dir)
    bbs, bbs_df = parse_bbs(img_paths)
    save_new_img(img, bbs, bbs_df, clsnum, o_width, o_height, prefix, output_dir)
    copy_all(dir_check, prefix, output_dir)


def beforehand():
    # 引数処理
    original_ndpi_path = sys.argv[1]
    cropped_imgs_dir = Path(sys.argv[2])
    o_width = int(sys.argv[3])
    o_height = int(sys.argv[4])
    prefix = sys.argv[5]
    output_dir = sys.argv[6]

    # 切り出し元画像をロード＋切り出し済み画像をロード
    img = openslide.OpenSlide(original_ndpi_path)
    clss = ["benign", "intermediate", "malignant"]
    img_paths = []
    for cls_ in clss:
        img_paths += (cropped_imgs_dir / cls_).glob("*.png")

    # クラス名とクラス番号を対応
    clsnum = {"benign": 0, "intermediate": 1, "malignant": 2}

    # 出力ディレクトリ
    dir_check = ["benign", "intermediate", "malignant",
                 "benign_bb", "intermediate_bb", "malignant_bb", "all"]
    return img, img_paths, clsnum, dir_check, o_width, o_height, prefix, output_dir


def make_output_dir(dir_check, output_dir):
    # 「new」ディレクトリの中にすべて出力
    save_dir = Path(output_dir)
    if not save_dir.exists():
        save_dir.mkdir()

    # 各クラスを保存するディレクトリと、
    # これに応じたバウンディングボックスを示すテキストファイルを保存する「*_bb」、
    # さらにすべてを保存する「all」
    for dir_ in dir_check:
        if not (save_dir / dir_).exists():
            (save_dir / dir_).mkdir()


def parse_bbs(img_paths):
    # それぞれの画像から、class, width, height, offsetx, offsetyを取得
    bbs = []
    bb = namedtuple("bb", ("cls", "stem", "suffix",
                           "width", "height",
                           "offsetx", "offsety",
                           "leftbottomx", "leftbottomy",
                           "rightupx", "rightupy",
                           "rightbottomx", "rightbottomy"))
    for path in img_paths:
        im = cv2.imread(str(path), 1)
        cls_ = path.parent.name
        name = path.stem
        suffix = path.suffix
        height, width, _ = im.shape
        offsetx = int(path.stem.split("_")[-2])
        offsety = int(path.stem.split("_")[-1])
        leftbottomx = offsetx
        leftbottomy = offsety + height
        rightupx = offsetx + width
        rightupy = offsety
        rightbottomx = offsetx + width
        rightbottomy = offsety + height
        bbdata = bb(cls_, name, suffix,
                    width, height,
                    offsetx, offsety,
                    leftbottomx, leftbottomy,
                    rightupx, rightupy,
                    rightbottomx, rightbottomy)
        bbs.append(bbdata)
    bbs_df = pd.DataFrame(bbs)
    return bbs, bbs_df


def save_new_img(img, bbs, bbs_df, clsnum, o_width, o_height, prefix, output_dir):
    for idx, bb in enumerate(bbs):
        # ランダムに切り出し範囲を拡大した画像を保存
        try:
            xleft = random.randint(0, o_width - bb.width)
            xright = o_width - xleft - bb.width
            yup = random.randint(0, o_height - bb.height)
            ybottom = o_height - yup - bb.height
            newwidth = bb.width + xleft + xright
            newheight = bb.height + yup + ybottom
            newoffsetx = bb.offsetx - xleft
            newoffsety = bb.offsety - yup

            region = img.read_region((newoffsetx, newoffsety),
                                     0,
                                     (newwidth, newheight))
            region.save(f"{output_dir}/{bb.cls}/{prefix}{bb.stem}{bb.suffix}")

            # 保存した画像に含まれるバウンディングボックスの有無を確認
            newrightx = newoffsetx + newwidth
            newrighty = newoffsety + newheight
            """
            print("newwidth", newwidth)
            print("newheight", newheight)
            print("newoffsetx", newoffsetx)
            print("newoffsety", newoffsety)
            """
            # 左上に来る場合の処理
            cond1 = bbs_df['rightbottomx'] > newoffsetx
            cond2 = bbs_df['rightbottomx'] < newrightx
            cond3 = bbs_df['rightbottomy'] > newoffsety
            cond4 = bbs_df['rightbottomy'] < newrighty
            check1 = bbs_df.loc[cond1]
            check2 = check1.loc[cond2]
            check3 = check2.loc[cond3]
            checkleftup = check3.loc[cond4]

            # 右上に来る場合の処理
            cond5 = bbs_df['leftbottomx'] > newoffsetx
            cond6 = bbs_df['leftbottomx'] < newrightx
            cond7 = bbs_df['leftbottomy'] > newoffsety
            cond8 = bbs_df['leftbottomy'] < newrighty
            check4 = bbs_df.loc[cond5]
            check5 = check4.loc[cond6]
            check6 = check5.loc[cond7]
            checkrightup = check6.loc[cond8]

            # 左下に来る場合の処理
            cond9 = bbs_df['rightupx'] > newoffsetx
            cond10 = bbs_df['rightupx'] < newrightx
            cond11 = bbs_df['rightupy'] > newoffsety
            cond12 = bbs_df['rightupy'] < newrighty
            check7 = bbs_df.loc[cond9]
            check8 = check7.loc[cond10]
            check9 = check8.loc[cond11]
            checkleftbottom = check9.loc[cond12]

            # 右下に来る場合の処理
            cond13 = bbs_df['offsetx'] > newoffsetx
            cond14 = bbs_df['offsetx'] < newrightx
            cond15 = bbs_df['offsety'] > newoffsety
            cond16 = bbs_df['offsety'] < newrighty
            check10 = bbs_df.loc[cond13]
            check11 = check10.loc[cond14]
            check12 = check11.loc[cond15]
            checkrightbottom = check12.loc[cond16]

            # いずれかを満たすものを結合
            check = pd.concat([checkleftup, checkleftbottom, checkrightup, checkrightbottom])
            check = check.drop_duplicates(["stem"])

            # 自分自身を除外
            cond_self = bbs_df['stem'] == bb.stem
            check = check.loc[~cond_self]
            # check.to_csv("check.csv")

            # アノテーションデータファイルに書き込み
            # ここで残っているBBは、四隅のうち少なくともひとつが、余白を追加した元BBに含まれている。
            # cnt = 0
            lines_to_write = []
            with open(f"{output_dir}/{bb.cls}_bb/{prefix}{bb.stem}.txt", "w") as annot:
                centerx = xleft + bb.width / 2
                centery = yup + bb.height / 2
                lines_to_write.append(f"{clsnum[bb.cls]} {centerx / newwidth} {centery / newheight} {bb.width / newwidth} {bb.height / newheight}\n")
                if not check.empty:
                    for line in check.itertuples():
                        # 追加したいBBの左上x座標が、余白追加BBの左上x座標より小さい場合は、余白追加BBの相対座標で0に合わせる
                        diff_offsetx = line.offsetx - newoffsetx
                        offsetx_line = diff_offsetx if diff_offsetx > 0 else 0
                        """
                        print("diff_offsetx", diff_offsetx)
                        print("offsetx_line", offsetx_line)
                        """

                        # 追加したいBBの左上y座標が、余白追加BBの左上y座標より小さい場合は、余白追加BBの相対座標で0に合わせる
                        diff_offsety = line.offsety - newoffsety
                        offsety_line = diff_offsety if diff_offsety > 0 else 0
                        """
                        print("diff_offsety", diff_offsety)
                        print("offsety_line", offsety_line)
                        """

                        # 追加したいBBの右下x座標が、余白追加BBの右下x座標より大きい場合は、余白追加BBの相対座標で横幅に合わせる
                        diff_rightbottomx = line.rightbottomx - newoffsetx
                        rightbottomx_line = diff_rightbottomx if diff_rightbottomx < newwidth else newwidth
                        """
                        print("diff_rightbottomx", diff_rightbottomx)
                        print("rightbottomx", rightbottomx_line)
                        """

                        # 追加したいBBの右下y座標が、余白追加BBの右下y座標より大きい場合は、余白追加BBの相対座標で縦幅に合わせる
                        diff_rightbottomy = line.rightbottomy - newoffsety
                        rightbottomy_line = diff_rightbottomy if diff_rightbottomy < newheight else newheight
                        """
                        print("diff_rightbottomy", diff_rightbottomy)
                        print("rightbottomy", rightbottomy_line)
                        """

                        # アノテーションデータ用に整形
                        width_line = rightbottomx_line - offsetx_line
                        height_line = rightbottomy_line - offsety_line
                        centerx_line = offsetx_line + width_line / 2
                        centery_line = offsety_line + height_line / 2
                        """
                        print("width_line", width_line)
                        print("height_line", height_line)
                        print("centerx_line", centerx_line)
                        print("centery_line", centery_line)
                        print(f"{clsnum[line.cls]} {centerx_line / newwidth} {centery_line / newheight} {width_line / newwidth} {height_line / newheight}\n")
                        """
                        lines_to_write.append(f"{clsnum[line.cls]} {centerx_line / newwidth} {centery_line / newheight} {width_line / newwidth} {height_line / newheight}\n")
                        # cnt = 1
                annot.writelines(lines_to_write)
                # if cnt == 1:
                #    sys.exit()
            print(idx)
        except Exception as e:
            from datetime import datetime
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(Path(__file__).parent.parent/"log/read_all_bb.log", "a") as log:
                log.write(f"[{now}][{e}][{bb}]\n")


def copy_all(dir_check, prefix, output_dir):
    print("coping")
    lst = []
    for dir_ in dir_check:
        root = Path(output_dir)
        one_dir = root/dir_
        lst += list(one_dir.glob(f"{prefix}*.png"))
        lst += list(one_dir.glob(f"{prefix}*.txt"))
    for path in lst:
        try:
            shutil.copy(str(path), root/"all")
        except shutil.SameFileError:
            pass


if __name__ == '__main__':
    run()
