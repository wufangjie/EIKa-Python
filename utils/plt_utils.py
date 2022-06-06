import numpy as np
import matplotlib.pyplot as plt


__all__ = ['ColorCycler', 'plt', 'set_plt_theme']


def cv2_imshow(winname, mat, is_rgb=False):
    """imshow(winname, mat) -> None"""
    plt.figure(winname, figsize=(5, 8))
    if len(mat.shape) < 3 or mat.shape[2] == 1:
        plt.imshow(mat, cmap='gray')
    elif is_rgb:
        plt.imshow(np.asarray(mat))
    else:
        plt.imshow(np.asarray(mat)[..., 2::-1])
    plt.axis('image') # tight, equal


class ColorCycler:
    def __init__(self, kind='seaborn'):
        if kind == 'mpl':
            self.seq = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        elif kind == 'seaborn':
            self.seq = ['#4c72b0', '#dd8452', '#55a868', '#c44e52', '#8172b3',
                        '#937860', '#da8bc3', '#8c8c8c', '#ccb974', '#64b5cd']
        elif kind == 'paired': # sns.color_palette("Paired")
            self.seq = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
                        '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
                        '#ffff99', '#b15928']
        else:
            raise Exception('Unknown color cycle: {}!'.format(kind))
        self.index = 0
        self.count = len(self.seq)

    def __getitem__(self, index):
        return self.seq[index % self.count]

    def __next__(self):
        color = self.seq[self.index]
        if self.index == self.count - 1:
            self.index = 0
        else:
            self.index += 1
        return color

    # @property
    # def current(self):
    #     return self.seq[self.index]

    def reset_index(self, index=0):
        self.index = index % self.count

    @classmethod
    def convert(cls, rgb_01_lst, kind='print'):
        """Convert rgb from 0~1 float to hex"""
        # TODO: more convert
        if kind == 'print':
            for rgb in rgb_01_lst:
                print('#{:02x}{:02x}{:02x}'.format(
                    *map(lambda x: int(round(255 * x)), rgb)))
        else:
            return ', '.join("'#{:02x}{:02x}{:02x}'".format(
                *map(lambda x: int(round(255 * x)), rgb))
                             for rgb in rgb_01_lst)

    def plot():
        raise NotImplementedError # TODO: just like sns.palplot


def set_plt_theme(override='default', insert_0=None):
    if override == 'default':
        override = {
            # 'axes.prop_cycle': plt.cycler('color', CC._color[:, 2]),
            'savefig.dpi': 300,

            'figure.titlesize': 28,
            'figure.titleweight': 'bold',

            'axes.titlesize': 28, # 'large'
            'axes.titleweight': 'bold', # 'normal'
            # it seems useless when there is no bold file?

            'figure.figsize': [16, 9], # [6.4, 4.8]
            'font.size': 16, # 10.0
            # 'figure.titlesize': 32, # 'large' # seems useless

            'legend.fontsize': 16, # 'medium' for font_scalings
            'lines.markersize': 7, # default 6 is good enough

            'xtick.labelsize': 16, # 'medium'
            'ytick.labelsize': 16, # 'medium'

            'axes.labelsize': 20, # 'medium'

            'grid.linestyle': '-.',

            'axes.unicode_minus': False,


            'xtick.bottom': True,
            'xtick.direction': 'in', # {in, out, inout}

            'ytick.direction': 'in',
            'ytick.left': True,

            'font.family': ['serif'],

        }
        # xtick.major xtick.minor 指坐标轴的主副刻度
    elif override == 'present':
        override = {
            # 'axes.prop_cycle': plt.cycler('color', CC._color[:, 2]),
            'savefig.dpi': 300,

            'figure.titlesize': 56,
            'figure.titleweight': 'bold',

            'axes.titlesize': 56, # 'large'
            'axes.titleweight': 'bold', # 'normal'
            # it seems useless when there is no bold file?

            'figure.figsize': [16, 9], # [6.4, 4.8]
            'font.size': 32, # 10.0
            # 'figure.titlesize': 32, # 'large' # seems useless

            'legend.fontsize': 32, # 'medium' for font_scalings
            'lines.markersize': 7, # default 6 is good enough

            'xtick.labelsize': 32, # 'medium'
            'ytick.labelsize': 32, # 'medium'

            'axes.labelsize': 40, # 'medium'

            'axes.linewidth': 2.4, # 0.8
            'lines.linewidth': 4.5, # 1.5
            'lines.markeredgewidth': 3.0, # 1.0

            'grid.linestyle': '-.',

            'axes.unicode_minus': False,

            'xtick.bottom': True,
            'xtick.direction': 'in', # {in, out, inout}

            'ytick.direction': 'in',
            'ytick.left': True,

            'font.family': ['serif'],
        }

    if insert_0 is None:
        # NOTE: need modify font_manager.py, add ttc support

        insert_0 = {
            #'font.monospace': 'Noto Sans Mono',
            'font.sans-serif': 'Noto Sans CJK JP',
            'font.serif': 'Noto Serif CJK JP'
        }
        #insert_0 = {}

    for key, val in override.items():
        plt.rcParams[key] = val

    for key, val in insert_0.items():
        if val not in plt.rcParams[key]:
            plt.rcParams[key].insert(0, val)
            #plt.rcParams[key] = [val]



# plt.set_theme = set_plt_theme
# plt.set_theme()



if __name__ == '__main__':


    x = np.linspace(0, 14, 100)
    fig = plt.figure()
    for i in range(7):
        plt.plot(x, (7 - i) * np.sin(x + i * 0.5),
                 label='{}sin(x+{})'.format(
                     7 - i, np.round(i / 2, 1).astype(str)))
    plt.xlabel('-xlabel')
    plt.ylabel('+ylabel')
    plt.legend(loc='best')
    #plt.legend(loc='upper right', shadow=True, bbox_to_anchor=(1, 0.5))
    plt.title('中文标题一定要长才好看')



    from matplotlib.font_manager import FontProperties
    font_title = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc', size=28)
    #font_title = FontProperties(fname='/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', size=28)

    plt.title('门庭若市 才高八斗', fontproperties=font_title)



if False:

    from matplotlib.font_manager import fontManager, _call_fc_list
    from matplotlib.font_manager import *
    import os

    def zh_call_fc_list():
        import sys
        import subprocess
        import six
        out = subprocess.check_output([str('fc-list'), ':lang=zh', '--format=%{file}\\n'])
        # fnames = []
        fnames = set()
        for fname in out.split(b'\n'):
            try:
                fname = six.text_type(fname, sys.getfilesystemencoding())
            except UnicodeDecodeError:
                continue
            # fnames.append(fname)
            fnames.add(fname)
        return fnames
    pprint(zh_call_fc_list())

    for i, font in enumerate(fontManager.ttflist):
    #for i, font in enumerate(createFontList(findSystemFonts())):#fontManager.ttflist):
        if 'noto' in font.fname.lower():
        # if (os.path.exists(font.fname)
        #     and os.stat(font.fname).st_size > 1e6):
            print(i, font.name)

    # findSystemFonts(paths) + findSystemFonts()
    # pprint(fontManager.ttffiles)

    # #fpath = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    # fpath = '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
    # font = ft2font.FT2Font(fpath)
    # print(font.family_name)

    temp = createFontList(findSystemFonts())

    pprint(createFontList(findSystemFonts()))

    for fname in _call_fc_list():
        if not os.path.splitext(fname)[1][1:] in ('ttf', 'otf'):
            print(fname)



if False:
    # origin font method
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
    font_exec = '''
    from matplotlib.font_manager import FontProperties
    font_path = '/usr/share/fonts/opentype/noto/'
    font_title = FontProperties(fname=font_path+'NotoSansCJK-Bold.ttc', size=32)
    font_label = FontProperties(fname=font_path+'NotoSansCJK-Regular.ttc', size=24)
    font_text = FontProperties(fname=font_path+'NotoSansCJK-Regular.ttc', size=20)
    '''


if False:
    # twin axes
    ax1 = plt.subplot(111)
    ax2 = ax1.twinx()

# default style
# /usr/share/matplotlib/mpl-data/stylelib/

# sns.set(style='white', context='notebook', palette='deep')
# sns.set_style(rc={'font.sans-serif': ['Yuan Mo Wen']})




# plt.subplots_adjust(left=0.05, right=0.95, bottom=0.08, top=0.95)

# * color
# ** 护眼色?
# | 颜色   | 代码    | 数值                 |
# |--------+---------+----------------------|
# | 银河白 | #FFFFFF | rgb（255，255，255） |
# | 杏仁黄 | #FAF9DE | rgb（250，249，222） |
# | 秋叶褐 | #FFF2E2 | rgb（255，242，226） |
# | 胭脂红 | #FDE6E0 | rgb（253，230，224） |
# | 青草绿 | #E3EDCD | rgb（227，237，205） |
# | 海天蓝 | #DCE2F1 | rgb（220，226，241） |
# | 葛巾紫 | #E9EBFE | rgb（233，235，254） |
# | 极光灰 | #EAEAEF | rgb（234，234，239） |

# ** excel 最舒服的背景色, matplotlib 画图
# | 浅蓝 | #a6cee3 |
# | 深蓝 | #2079b4 |
# | 浅绿 | #b0dd8b |
# | 深绿 | #36a12e |
# | 浅红 | #fb9898 |
# | 深红 | #e31b1c |
# | 浅褐 | #cfa256 |
# | 深褐 | #995d13 |
# | 浅黄 | #fae371 |
# | 深黄 | #feb308 |
# | 浅紫 | #cc99ff |
# | 深紫 | #9b59bd |
