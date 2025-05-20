#!/usr/local/bin/python

import sys
import argparse

# globals
parser = argparse.ArgumentParser(description='Planetary gear calculator')
args = None

# command line options
class OPTIONS:
    EVEN_SPACING="e"
    PRINT_HEADER="nh"
    PRINT_ALL="so"
    PRINT_TPS = "tps"
    PRINT_TPR = "tpr"
    PRINT_TSR = "tsr"
    PRINT_ANG = "ang"

# program configuration
class CONFIG:
    ring   = 0
    planet = 0
    sun    = 0
    limit  = 50
    print_header = False
    print_tps    = False
    print_tpr    = False
    print_tsr    = False
    print_angle  = False
    min_teeth = 4

    # transform command line options into program configuration
    @staticmethod
    def from_options(options):

        # print only what is requested
        if OPTIONS.PRINT_ALL in options:
            CONFIG.print_header = True
            CONFIG.print_angle = True
            CONFIG.print_tpr = True
            CONFIG.print_tps = True
            CONFIG.print_tsr = True
            CONFIG.print_ang = True
        else:
            if OPTIONS.PRINT_TPR in options:
                CONFIG.print_tpr = True
            if OPTIONS.PRINT_TPS in options:
                CONFIG.print_tps = True
            if OPTIONS.PRINT_TSR in options:
                CONFIG.print_tsr = True
            if OPTIONS.PRINT_ANG in options:
                CONFIG.print_angle = True

        # no header option
        if OPTIONS.PRINT_HEADER in options:
            CONFIG.print_header = True

        # gear configuration
        try:
            R,P,S = str(args.gear).split(':',3)
        except:
            warning("Invalid gear configuration format")
            exit()

        CONFIG.ring   = convert_to_int(R)
        CONFIG.planet = convert_to_int(P)
        CONFIG.sun    = convert_to_int(S)

        # copy configurations limit
        CONFIG.limit = args.limit
        if CONFIG.limit == 0:
            warning("Invalid number of configurations (0)")
            exit()

        # copy min_teeth
        CONFIG.min_teeth = args.min_teeth

#
# helper functions
def print_full_help():
    """打印完整的程序选项和使用说明"""
    print("""
行星齿轮计算器 - 完整使用说明
============================

基本格式:
  python plgcalc.py R:P:S [选项]

参数说明:
  R:P:S       齿轮配置格式(齿圈:行星轮:太阳轮)
              示例: 36:14:8 或 42:18: (生成太阳轮) 或 ::12 (生成齿圈和行星轮)

主要选项:
  -l, --limit N   限制生成的配置数量 (默认: 50)
  -p, --planets N 指定行星轮数量
  -e, --even-spacing 只显示行星轮均匀分布的配置
  --min-teeth N   设置最小齿数 (默认: 4)

输出选项:
  --tps       显示行星轮-太阳轮传动比(齿圈固定)
  --tpr       显示行星轮-齿圈传动比(太阳轮固定)  
  --tsr       显示太阳轮-齿圈传动比(行星轮固定)
  --ang       显示太阳轮-行星轮角度关系
  -a, --all   显示所有计算数据
  -hdr, --header 显示配置表头

示例:
  1. 验证配置: python plgcalc.py 36:14:8
  2. 生成10种配置: python plgcalc.py 42:18: -l 10
  3. 均匀分布配置: python plgcalc.py ::8 -l 10 -e -p 3
    """)
# 可以添加输入验证逻辑
def convert_to_int(string):
    """将字符串转换为整数，无效输入返回0"""
    try: 
        num = int(string)
        return num if num >= 0 else 0
    except: 
        return 0


def warning(warn):
    sys.stderr.write("Warning: %s\n" % warn)
    #print warn

def valid_planetary(ring, planet, sun, even_planets):
    # check if R = 2 * P + S
    """
    验证行星齿轮配置是否有效
    参数:
        ring: 齿圈齿数
        planet: 行星齿轮齿数
        sun: 太阳轮齿数
        even_planets: 行星齿轮数量(用于均匀分布检查)
    返回:
        bool: 配置是否有效
    """
    if ring != 2 * planet + sun:
        return False

    if even_planets is not None:
        if ring % even_planets != 0 or sun % even_planets != 0:
            return False # planets are not even

    return True

#
# print functions
#

def print_header():

    if CONFIG.print_header == False:
        return

    prs1 = "Gear\t"
    prs2 = "Configuration"

    if CONFIG.print_tps:
        prs1 = prs1 + "\tTp/Ts Ratio"
        prs2 = prs2 + "\tRing fixed"

    if CONFIG.print_tpr:
        prs1 = prs1 + "\tTp/Tr Ratio"
        prs2 = prs2 + "\tSun fixed"

    if CONFIG.print_tsr:
        prs1 = prs1 + "\tTs/Tr Ratio"
        prs2 = prs2 + "\tPlanets fixed"

    if CONFIG.print_angle:
        prs1 = prs1 + "\tAngle"
        prs2 = prs2 + "\tPlanet-Sun"

    print(prs1)
    print(prs2)

def print_entry(ring,planet,sun):

    # Ratio formula:
    # ( R + S ) * Tp = R * Tr + S * Ts
    # => Ring    fixed : Tp/Ts = S / (R+S)
    # => Sun     fixed : Tp/Tr = R / (R+S)
    # => Planets fixed : Ts/Tr = - R / S

    prs = "%.2u:%.2u:%.2u" % (ring,planet,sun)

    if CONFIG.print_tps:
        prs = prs + "\t%f" % (sun / float(sun+ring))

    if CONFIG.print_tpr:
        prs = prs + "\t%f" % (ring / float(ring+sun))

    if CONFIG.print_tsr:
        prs = prs + "\t%f" % (ring / float(sun) * (-1.0))

    if CONFIG.print_angle:
        prs = prs + "\t%f" % (360 / float(ring+sun))

    print(prs)

def print_examples():
    print ('''
    1. Check if the following configuration is correct:
        ring gear   = 36 teeth
        planet gear = 14 teeth
        sun gear    = 8 teeth

    > plgcalc.py 36:14:8

    2. Check 10 configurations that are possible for a planetary having:
        ring gear   = 42 teeth
        planet gear = 18 teeth

    > plgcalc.py 42:18: -l 10

    3. Same thing for a planetary that has:
        sun gear    = 12 teeth

    > plgcalc.py ::12 -l 10

    3. Generate all possible configurations for a planetary gear set with following params:
        sun gear    = 9 teeth
        planets     = 3 (evenly spaced)

    > plgcalc.py ::8 -l 10 -e -p 3
    ''')

# check command line arguments
def prepare_arguments():
    global parser

    parser.add_argument(
            'gear',
            metavar='R:P:S',
            type=str,
            help='Configuration of planetary gears')

    parser.add_argument(
            '--examples',
            metavar="",
            help='Print some usage examples as extended help')

    parser.add_argument(
            '-l','--limit',
            type=int,
            default=50,
            metavar="L",
            help='Limit of configurations to be calculated (default 50)')

    parser.add_argument(
            '-p','--planets',
            type=int,
            default=0,
            metavar="P",
            help='Number of planet gears')

    parser.add_argument(
            '-e','--even-spacing',
            dest='options',
            action='append_const',
            const=OPTIONS.EVEN_SPACING,
            help="Show results only for planets evenly spaced")

    parser.add_argument(
            '-hdr','--header',
            dest='options',
            action='append_const',
            const=OPTIONS.PRINT_HEADER,
            help="Print configurations header for better description")

    parser.add_argument(
            '-a','--all',
            dest='options',
            action='append_const',
            const=OPTIONS.PRINT_ALL,
            help="Print out complete configuration data")

    parser.add_argument(
            '--tps',
            dest='options',
            action='append_const',
            const=OPTIONS.PRINT_TPS,
            help="Print planet-sun ratio (ring fixed)")

    parser.add_argument(
            '--tpr',
            dest='options',
            action='append_const',
            const=OPTIONS.PRINT_TPR,
            help="Print planet-ring ratio (sun fixed)")

    parser.add_argument(
            '--tsr',
            dest='options',
            action='append_const',
            const=OPTIONS.PRINT_TSR,
            help="Print sun-ring ratio (planets fixed)")

    parser.add_argument(
            '--ang',
            dest='options',
            action='append_const',
            const=OPTIONS.PRINT_ANG,
            help="Print sun-planets angle")

    parser.add_argument(
            '--min-teeth',
            type=int,
            default=4,
            metavar="P",
            help='Minimum number of teeth to use when generating configurations (default: 4)')

def parse_input_params():
    global args, parser
    # parse arguments
    prepare_arguments()
    # 检查是否有RPS参数，没有则提示用户输入
    if len(sys.argv) == 1:  # 只有脚本名没有参数
        print_usage()
        user_input = input("请输入齿轮配置(R:P:S): ").strip()
        if not user_input:
            print("错误: 必须输入齿轮配置")
            sys.exit(1)
        sys.argv.append(user_input)
    args = parser.parse_args()
    # validate input
    if args.options is None: args.options = []

    CONFIG.from_options(args.options)

# print usage
def usage():
    parser.print_help()

# generate all possible configuration for planetary
def generate_possible_configurations(ring, planet, sun):

    cnt_defined = 0
    result = None
    even_planets = None

    if ring != 0: cnt_defined = cnt_defined + 1
    if planet != 0: cnt_defined = cnt_defined + 1
    if sun != 0: cnt_defined = cnt_defined + 1

    if args.options is not None and OPTIONS.EVEN_SPACING in args.options:
        if args.planets == 0:
            return "define number of planets, or remove even option"
        even_planets = args.planets


    #
    # all set - just validate configuration
    #
    if cnt_defined == 3:
        if valid_planetary(ring, planet, sun, even_planets):
            return [(ring,planet,sun)]
        else:
            return "invalid gear configuration"

    #
    # two set - one to calculate
    #
    if cnt_defined == 2:
        # calculate ring
        if ring == 0:
            ring = 2 * planet + sun
        # calculate planet
        elif planet == 0:
            planet = ring - sun
            if planet % 2 != 0:
                return "invalid planet, adjust ring or sun"

            planet = planet//2
        # calculate sun
        elif sun == 0:
            sun = ring - planet * 2

        if valid_planetary(ring, planet, sun, even_planets):

            if ring == 0 or planet == 0 or sun == 0:
                return "invalid gear configuration (0 teeth)"

            return [(ring,planet,sun)]
        else:
            return "invalid gear configuration"

    #
    # one set - two to generate
    #
    if cnt_defined == 1:

        result = []

        # RING set => generate possible PLANET and SUN
        if ring != 0:

            # check even spacing option
            if even_planets is not None:
                if ring % even_planets != 0:
                    return "invalid ring configuration, planets will never be evenly spaced"

            limit = CONFIG.limit

            for p in range(CONFIG.min_teeth, ring/2 - CONFIG.min_teeth + 1):
                if valid_planetary(ring,p,ring - 2 * p,even_planets):
                    if limit : limit = limit - 1
                    result.append((ring,p,ring - 2 * p) )
                    if limit == 0 : break

        # SUN set :) => generate possible RING and PLANET
        # need additional turn ration TRP (RING/PLANET) set
        if sun != 0:

            # check even spacing option
            if even_planets is not None:
                if sun % even_planets != 0:
                    return "invalid sun configuration, planets will never be evenly spaced"

            p = CONFIG.min_teeth
            limit = args.limit

            while( True ):
                if valid_planetary(sun + p * 2, p, sun, even_planets):
                    result.append((sun + p * 2, p, sun))
                    limit = limit - 1

                # decrement limit
                if limit == 0: break
                p = p + 1

        if planet != 0:
            # check even spacing option
            if even_planets is not None:
                if planet % even_planets != 0:
                    return "invalid planet configuration, planets will never be evenly spaced"

            s = CONFIG.min_teeth
            limit = args.limit

            while( True ):
                if valid_planetary(planet*2+s,planet,s,even_planets):
                    result.append((planet*2+s,planet,s))
                    limit = limit - 1

                # break on limit
                if limit == 0: break
                s = s + 1

    return result

def print_usage():
    """打印程序使用说明"""
    print("""
行星齿轮计算器使用说明：
1. 基本格式: R:P:S (齿圈:行星轮:太阳轮齿数)
2. 示例:
   - 验证配置: 36:14:8
   - 生成配置: 42:18: (生成可能的太阳轮配置)
   - 生成配置: ::12 (生成可能的齿圈和行星轮配置)
3. 选项:
   - -l N: 限制生成配置数量
   - -p N: 指定行星轮数量
   - -e: 只显示均匀分布的配置
    """)


if __name__ == "__main__":
    # 只在没有参数时才显示使用说明和提示输入
    if len(sys.argv) == 1:
        print_usage()
        user_input = input("请输入齿轮配置(R:P:S): ").strip()
        if not user_input:
            print("错误: 必须输入齿轮配置")
            sys.exit(1)
        sys.argv.append(user_input)
    
    # 帮助选项处理
    if "-h" in sys.argv or "--help" in sys.argv:
        print_full_help()
        exit()
    
    # 示例选项处理
    # EXAMPLES
    if "--examples" in sys.argv:
        print_examples()
        exit()

    # PARAMETERS
    parse_input_params()

    # CONFIGS
    results = generate_possible_configurations(CONFIG.ring,CONFIG.planet,CONFIG.sun)

    # printout error
    if results == None or len(results) == 0:
        warning("No results possible")
    elif type(results) == str:
        warning("No results possible: %s" % results)
    else:

        # print header
        print_header()

        # results
        for res in results:
            print_entry(res[0],res[1],res[2])
