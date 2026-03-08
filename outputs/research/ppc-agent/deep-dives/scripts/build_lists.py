"""Build curated negative list for campaigns 4-6 and un-negate list for campaigns 1-3."""
import json, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

BASE = "c:/Users/barta/OneDrive/Documents/Claude_Code_Workspace_TEMPLATE/Claude Code Workspace TEMPLATE"

with open(f'{BASE}/outputs/research/ppc-weekly/data/search-terms-14d-2026-03-02.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

UNPROTECTED = {
    'CATCH ALL NGO - OLD': 'Cmp4',
    'Catch All - Auto - 0.15 - incrementum': 'Cmp5',
    'catch all - auto - 0.19 incrumentum': 'Cmp6',
}
PROTECTED = {
    'Catch All - Auto - 0.39 - Incrementum': 'Cmp1',
    'Catch All - Auto - 0.49 - Incrementum': 'Cmp2',
    'Catch All - Auto - 0.29 - Incrementum': 'Cmp3',
}
ALL_CATCHALL = {**UNPROTECTED, **PROTECTED}

# Performance across all catch-all campaigns
all_perf = defaultdict(lambda: {'cost': 0, 'sales': 0, 'orders': 0, 'clicks': 0, 'impressions': 0})
unp_perf = defaultdict(lambda: {'cost': 0, 'sales': 0, 'orders': 0, 'clicks': 0, 'impressions': 0})
prot_perf = defaultdict(lambda: {'cost': 0, 'sales': 0, 'orders': 0, 'clicks': 0, 'impressions': 0})

for row in data:
    cn = row.get('campaignName', '')
    if cn in ALL_CATCHALL:
        term = row.get('searchTerm', '').lower().strip()
        all_perf[term]['cost'] += float(row.get('cost', 0))
        all_perf[term]['sales'] += float(row.get('sales7d', 0))
        all_perf[term]['orders'] += int(row.get('purchases7d', 0))
        all_perf[term]['clicks'] += int(row.get('clicks', 0))
        all_perf[term]['impressions'] += int(row.get('impressions', 0))
    if cn in UNPROTECTED:
        term = row.get('searchTerm', '').lower().strip()
        unp_perf[term]['cost'] += float(row.get('cost', 0))
        unp_perf[term]['sales'] += float(row.get('sales7d', 0))
        unp_perf[term]['orders'] += int(row.get('purchases7d', 0))
        unp_perf[term]['clicks'] += int(row.get('clicks', 0))
        unp_perf[term]['impressions'] += int(row.get('impressions', 0))
    if cn in PROTECTED:
        term = row.get('searchTerm', '').lower().strip()
        prot_perf[term]['cost'] += float(row.get('cost', 0))
        prot_perf[term]['sales'] += float(row.get('sales7d', 0))
        prot_perf[term]['orders'] += int(row.get('purchases7d', 0))
        prot_perf[term]['clicks'] += int(row.get('clicks', 0))
        prot_perf[term]['impressions'] += int(row.get('impressions', 0))

# Load negatives
neg1 = set()
neg2 = set()
neg3 = set()

# Read from the API data we already have (saved as JSON)
import os
neg_dir = f'{BASE}/outputs/research/ppc-agent/portfolio-action-plan/data'
os.makedirs(neg_dir, exist_ok=True)

# The negative terms were extracted from the API. We'll hardcode the key ones.
# (Full lists were displayed in API output earlier)
# For efficiency, load from the search term cross-ref: any term negated = term that appears
# in the negative keyword lists from campaigns 1-3

# Campaign 1 negatives (215 terms)
neg1_list = ['hama beads kit','beads','beados','sewing kit for kids ages 8-12','beads bulk','needlepoint kits','cross stitch kit','iron beads','hama beads','embroidery kit','punch needle','beads kit','perler bead pegboard','embroidery for kids','embroidery','latch hook kit','fuse beads kit','embroidery kits','mini perler beads','cross stitch kits for beginners','fuse beads','cross stitch kits for kids','embroidery kits for adults','cross stitch','beads for pens','perler beads kit','aqua beads kit','counted cross stitch kits for kids','marvel cross stitch kits','melty beads','perler beads set','latch hook kits for adults','beads for crafts','cross stitch kits','unicorn cross stitch kit','mini beads','stitch and zip needlepoint kits','rave beads','small beads','cross stitch kits for adults','adult perler beads','arts and crafts kit','aquabeads','arts and crafts','22000 perler beads','art & craft kit for cross stitch','artkal beads','24000 fuse beads kit','aquabeads refills','adult crafts','adjustable punch needle','marvel cross stitch','baby boy embroidery kit','small perler beads','kids needlepoint kits for beginners','latch hook canvas','curler beads','big bead kit','mini iron','knitting starter kit','indian bead kit','mini perler beads pegboards','embroidery pattern transfers','fuse beads bulk','bordar a mano kits','2.6 mm perler beads','sewing for kids ages 8-12','small latch hook kit','perler beads kit for adults','sewing for kids','perler bead kits for adults','kids cross stitch','cross stitch embroidery kits for adults','polly beads','large pony beads','bead kit','small plastic beads for crafts','hama beads set','fairy plush','perler beads pack','embroidery kit for beginners kids','sewing craft kit','bead kits','sewing patterns for beginners','needlepoint kit for kids','craft kits for kids 8-12','crafts for girls ages 8-12','fuse beads pegboards','hama beads kits','perler beads kit for kids','mini perler beads kit','sewing kit for kids','beginners cross stitch kits for kids','stamped cross stitch kits for beginners','learn to sew kit for kids ages 8-12','micro beads for slime','sewing kit','star wars embroidery kit','embroidery stitch practice kit','beginner cross stitch for kids','art kits for kids 9-12 girls','embroidery kit for beginners','kids sewing kit for beginners','hook rug kits for kids','latch kits','crafts for kids','beads for ironing crafts','fused beads kit','pencil case','perler+bead','cross stitch for kids ages 4-8','perler beads big','quefe beads','latch kit','mini counted cross stitch kits','cross stitching for kids','stamped cross stitch kit','beginner sewing kit','cross stitch accessories','needlepoint kits for beginners','bead sets','perler bead','unicorn craft','embroidery sets for adults','cross stitch supplies','fuse bead pegboard','disney cross stitch','embroidery pen','perler patterns','hammer beads','cartoon beads','embroidery kit for beginners adults','sewing kit for beginners','cooper beads','sewing craft kits for kids','unicorn latch hook kits for kids','latch hook kids','sew kit','rug making kit for kids','11 count cross stitch kits','perler bead activity kit','ballerina crafts for girls','latch hook kit for kids','cat cross stitch kits','super small beads','hama','kinetic beads','humidifier beads','sewing kit for adults','pink perler beads','teacher cross stitch','artkal mini beads','beginner cross stitch kit','melt beads','mini perlers','sew kit craft','beginner cross stitch kits for kids','embroidery sampler kit','stamped cross stitch kits','beads for mexican bracelets','sewing kits for kids','stamped latch hook kits','panda cross stitch kits','beginner cross stitch kits','embroidery pattern elephant','embroidery kit kids','huge bead kit','liquid beads','go create beads','needlepoint kids','mini perler bead kits','water fuse beads kit','tila bead kit','mini perler beads set','cross stitch kits for boys','ballerina craft','needlepoint kits for kids','disney cross stitch kits','kids embroidery kits','perler bead bulk','fusible beads for kids','magical crafts','latch hook','aqua beads','perler bead supplies','rice beads','latch and hook kids','bead art','mini fuse beads kit','micro beads','sewing kit for beginner','peyote beads','perler bead packs','perler bead patterns','poly beads','avengers cross stitch','fuze beads','felt sewing kit','cross stitch craft kit','counted cross stitch kits for adults','cross stitching kits','perler bead pack','cross stitch kit art','purl beads','learn to sew','latch hook kits for kids ages 8-12','loom kit for kids ages 8-12','needlepoint','perler beads storage','punto de cruz kit','latch hook rug kits for kids','perler mini beads','cross stitch beginner kit','locker hooking needle','dinosaur cross stitch kits']
neg1 = set(x.lower().strip() for x in neg1_list)

neg2_list = ['kids beginner cross stitch kits','kids cross stitch kit','perler bead storage','perler patterns','melting beads for kids','fuse beads pegboards','tweezers for crafts','kid latch hook kits for kids','kids sewing','hama beads 5mm','hama','fuse bead kit','iron beads for kids kit','perler bead kits','kid cross stitch kits for beginners','perler beads set','cross stitch kits kids','perler beads patterns','fairy craft kit','crafts','stamped cross stitch kits for adults','craftiloo latch hook kits for kids','craft kit','perler kits','beados','sewing kit for kids','crafts for girls ages 8-12','mini beads','needlepoint','cross stitch kit','embroidery kit','hama beads kit','fairy garden kit for kids','punch needle','embroidery patterns','beados kit','embroidery kits for kids','embroidery for kids','beginner cross stitch','bead kit','bulk beads','kids embroidery kit','jewelry making kit','crafts for adults','cross stitch for kids','stamped cross stitch','cat cross stitch kits','felt sewing kit','cross stitch kits for beginners','punch needle kits adults beginner','perler bead','fuse beads','needlepoint kit','embroidery kits for adults','perlers','mini perler','stamped cross stitch kits','beginner cross stitch kits for kids','sewing kit','latchkits','perler beads pegboards','needlepoint kits for kids','fairy plush','latch hook pencil case','latch kits','needlepoint for beginners','perler bead iron','kids sewing kit','learn to embroidery kit for kids','cross stitch backpack charms','embroidery for beginners','embroidery kit kids','needlepoint cat for kids','beginner needlepoint kits for adults','ballerina craft','felt sewing kit for kids','sewing kits for kids','melting beads','bead melting kit','kids sewing patterns for beginners','mini perler beads kit','perler beads 2.6mm','melting beads for kids crafts','perler bulk','latch and hook kit','mini melting beads','bead kits','kids latch hook','beginner sewing','cat embroidery kit','mini perler beads pegboard','melty beads kit','beados kits','perler beads kit for kids','cat cross stitch','printed cross stitch kits','punch needle kit for beginners','perler pegboard','beginner embroidery kit','melting bead','mini perler bead kit','latch hook rug kits for kids','beginner embroidery','learn embroidery kit','stamped cross stitch kits for beginners','sewing craft kit','needlepoint for kids','kid sewing kit','beginner cross stitch kit','mini fuse beads kit','embroidery punch needle','cross stitch kit for kids','beads for kids','embroidery kits for adults for beginners','pencil case','iron beads','hook and latch kit','bead','hook rug kits for kids','elephant embroidery','bead melting craft kit','mini iron for crafts','kids embroidery kits for beginners','perler mini','fuse beads bulk','crafts for girls','aquabeads','perler bead tweezer','fairy garden kit','embroidery kit for beginners adults','kids printed cross stitch','latch hook kit for kids','latch hook rug kit','sewing patterns for beginners','kid embroidery kit','ballerina crafts for girls','sew mini treats','sewing patterns for kids','cross stitch beginners kit','cross stitch kids','embroidery kits for girls','beads kits','cross stitch patterns','sewing projects','mini iron','melty beads pegboards','iron on beads for kids crafts','beads in bulk','perler bead mini','unicorn latch hook kit','latch kit for kids','sewing kit for beginners','sewing crafts for kids','punch art kit for kids','latch hook for kids','kids crafts','crafts for kids','cross stitch kits for beginners kids','beads for melting','beads','punch embroidery kit','needlepoint kids','sewing kit for adults','hama bead','aqua beads','aquabeads refills','beads for crafts','beginner embroidery kit for adults','perler mini beads','latch hook','perler bead patterns','perler beads bulk','melty beads','perler bead kit','pegboards for perler beads','latch hook kit pillow','qixels 3d','small bead','fuse beads mini','stamped cross stitch kids','beads mini','perler beads tools','beads iron','perler melting beads','perler bead colors','aqua tool set','stitch kits for kids','latch hook rug kits pencil','aquabeads maker','embroidery for beginners girls','pyssla','kids cross stitch pattern','fuse beads 2.6mm','stitch kit for kids','beginner sewing kit','kids beginner stamped cross stitch','kids cross stitch','fuze beads kit','2.6mm pegboard','mini perler beads pegboard 2.6mm','embroidery craft','easy sewing bag','easy sewing pattern','cross stitch kits for adults','kids beginners sewing kit ballerina','kids cross stitch kits for beginners','rug hooking kit for an 8 year old','perler pen','aquabeads kit','beginner needlepoint for girls','aquabeads sets','cross stitch baby quilt kits stamped','latchkits latch hook kits for kids','arts and crafts','craft iron','stamped for kids','perler beads storage','perler bead 6000 pack','stamped cross stitch beginner','iron beads kit','animal cross stitch kits','beginner cross stitch kits for adults','elephant cross stitch','bulk color perler','perler kits for adults','perler bead beads','pixelator beads','pre stamped embroidery','aqua beads craft set for girls','stitch and zip needlepoint kits','pixels beads','10 pre stamped embroidery patterns for beginners','printed cross stitch','craft storage','sewing for kids','beginner stitch kit','iron bead kit','perler beads big 5mm','cross stitch pre printed','dancer craft','latch rug','beginner cross stitch for kids','mini fuse beads 2.6mm','beads 1000 pcs','pegboard bracelet','knit kit for beginners kids','marvel bead kit','rug hooking supplies','pre printed cross stitch kits for kids','aqua beads refill with patterns','fuse beads perler','fuse melty beads','mini craft iron','hook latch rug kits for kids','bead kits mini','felt pillow fairies','rug knitting kit','fuse pearls','hama beads mini','kid cross stitch','aquabeads with water','mini beads perler','hama beads 2.6mm','perler beads set bulk','punch needle kit','cross stitching unicorn','pearl beads 22000','locker hooking','crafts beads','kids dog crafts','storage for beads','perles bracelet','fairy dolls','plush craft pillow','mini bead kit','iron melty beads','perles','crochet kit for beginners','fuse beads bucket','cross stitch','kids latch hook kit','embroidery beginners kit','fairy doll','cross-stitch stamped kits','locker hook','kids fairy crafts','cross stitch for kids beginners','felt fairy','art & craft kit for cross stitch','adult craft kits','cross stitch kits sewing','embroidery patterns to learn','rug hooking kits','beads you iron','perler beads black','dog needlepoint kits','hook rug for kids ages 8-12','mini bead melting craft kit','loom','adult punch needle kit','stitch and zip needlepoint','cross stitch patterns for beginners','kids needlepoint kits for beginners','puppy embroidery kits','smiley beads','needlepoint bag','cupcake latch hook kit','latch hook crochet set','bracelet kit together','perler beads beads','cross stitch for beginners','embroidery coin purse kit','embroidery','aqua beads pens','bead kits bulk','bead art','iron shapes crafts','cross arts and crafts','iron making beads','bulk perler beads','mini hama beads','no iron fuse beads','mini fuse beads pegboard','tweezers perler','dog cross stitch kits','plush crafts for kids','needlepoint kits for beginners','perler beads mini beads kit','bead pegboards','easy cross stitch kits for teens','bead kit bulk','melting plastic crystals','smiley face beads','kit beads','stamped cross stitch kits for beginners superhero','boy elf','preprinted needlepoint wallet kits','bead art picture kit','crochet hooks','aquabeads kit for adults','needlepoint kits for beginners unicorn small','hama melty','felt crafts','bead kits for teens','pixel art','qixels','mini beads iron','pre printed cross stitch kits','fairy little','embroidery needles child','pokemon stencils','latch hook kits bag','girls crafts','bead perler','beads pixel','sewing patterns for dogs','perler bead pegboard kit','fairy craft','qixels 3d beads','latch hook rugs for beginners','craft cases','aqua beads refill','latchkits for kids ages 8-12','water aquabeads set','adult cross stitch kits','kids mermaid cross stitch','hama bead mini','fairy garden','beginners stamped cross stitch kits','stamped cross stitch kits for kids','patterns for kids','beginners latch hook kit for kids','beads stencil','perler color','needlepoint for kids ages 8-12','cross stitch cat','rug sewing kit','purple smiley faces for bracelets','melty beads black','latch hook kits for adults','bead pack 11000','kid stitch cross stitch kits','latch hook kits for kids ages 8-12','aqua bead refills','easy needlepoint kits for adults','bracelets kit heat','fuse and perler beads','perler beads stencils','sewing pattern kits for beginners','craft kit adult','fuze beads','hama beads 5mm kit','latch hook kits unicorn','rice beads','large aquabeads kits','aqua beads refill pack','bead iron','fuze bead bracelet set','hama mini beads','latch hook kit age 6','heat fuse beads big','unicorn craft kit','fuse pegboards','kids needlepoint','sewing for beginners','bulk aqua beads 1000','beads perler','learn embroidery stitches kit','aquabeads refill pack','craft set','latch hook kit for beginners kids','mini perler beads','iron craft','craft beads','besds','rave beads','needlepoint kits for kids beginners','perle bracelet','5mm perler beads','sew your own','sewing patterns','beads of stitch','48 colors mini perler beads','beginning cross stitch kits for adults','bead that you iron','pixel paper','mini perler kit','2.6mm perler beads']
neg2 = set(x.lower().strip() for x in neg2_list)

neg3_list = ['pixo bitz','aquabeads refills','latch hook kit','latch hook kits for adults beginners','aqua beads','enchantimals','fairy plush','latch hook kits for adults','aquabeads','moulin roty','pixobitz','fuse beads','stamped cross stitch kits for adults clearance pillow cases','fairy garden kit for kids','learn to embroider kit adult beginner','rave beads','micro beads for resin','kandi beads','latch hook rug kits','stick and stitch embroidery paper','latch hook kits','fairy toy','cross stitch kits easy','fairy','latch hook pillow kit','the woobles','needlepoint kits for adults','embroidery kits for kids','mini fuse beads','loom kit','funzo beads','loom knitting','qixels refill','paper chain','fairies','magnetic beads','big perler beads','beads that you iron','perler beads kit','easter crafts','fairy dolls','pixel art','fairy toys','latch hook rug kits for adults','loom','chaquiras para pulseras','crochet keychain hooks','needlepoint kits for beginners','latch kits for kids','embroidery kit','hama beads','maileg mouse','rainbow loom rubber bands','yarn for kids ages 8-12','kids needlepoint kits for beginners','needle point kits for beginners','tiny perler beads','aquabeads kit','cross stitch kits for kids','embroidery kit for beginners','aquabeads refill','waldorf','playmobil mermaid','playmobiles for girls','easy sewing patterns for beginners kids','mostacillas para bisuteria al por mayor','perler caps','doll patterns for sewing','latch hook kit kids','fuse beads kit','punch needle','stitch and zip needlepoint kits','cross stitch corgi kit','beads for kids crafts','perler beads tools','embroidery kits for adults','beginner sewing patterns','crochet kit for beginners','miyuki beads','perler bead pegboard','girl potion kits','beginner cross stitch kits for kids','make your own stuffed animal kit','beados machine','knitting for kids','iron beads for kids kit','perler beads pegboards','knitting loom','punch needle kits adults beginner','punto de cruz libros','perler beads set','sewing kit for kids','easy sewing patterns for beginners','stitch and zip needlepoint kit','quilling kit','kids latch hook kit','fairy doll','perler','rice beads','polly pocket fairy','weaving loom for adults','knitting kit for beginners','punch rug kit','fuse beads 5mm 48 colors','aqua beads refill','cross stitch kits','qixels','stick and stitch embroidery designs','latch kit','punch needle embroidery kits','rainbow loom 2in1','expanded polystyrene beads','aqua beads kit','small beads','mini melt beads','levlovs','5mm fuse beads','hook and latch kit for adults','fuse beads set','mini perler beads','weaving loom for kids','tupalizy beads','quilt kits for beginners','mini perler bead kit','knitting kit','embroidery patterns transfers','latch hook kits for kids ages 8-12','cross stitch kits for adults','crossstitching kits adult','knitting looms','tri shaped beads','connecting beads','disney cross stitch kits','aquadots','spiderman cross stitch','cross stitch kits for beginners adults','art supplies for kids 9-12','bead art','needlepoint canvas','melty beads kit','crafts for girls ages 8 12','color pencil kit','plastic canvas purse kit','beading kit','fuse bead kit','glow in the dark beads','beads','133821019x','beado','biggie beads','beads for kids','craft kit','beeds','bead melting craft','beados teeneez','bracelet making kit crystal beads','aquabeads superhero','2.6 mm beads','beados','5 mm melt beads','beginners latch hook','bracelets kit marvel beads','aquabeads with water','children\'s latch kits','beginner punch hand embroidery','aquabeads spiderman','counted cross stitch kits for adults','aquabeads templates','beados studio','bracelet making kit for boys 5-7','craft kits for girls ages 10-12','bead needlepoint kits for kids','bead board','beginning cross stitch kits for kids boys','aquabeads for boys','beados refill','beginners cross stitch with printed canvas','bead bracelet kit','cool gifts for a 9 year old girl','beginners needlepoint kits for adults','butterfly diamond art','coin purse embroidery kit','box of beads','cheap crochet quilt kit','baeds','child sewing kit 9 year old','counted cross stitch kits for beginners','beginning knitting loom kit for kids','adult fuse beads kit','black fuse beads 5mm','bright fairy friends','baby announcement cross stitch','beginning embroidery','bead sets','build a bear clothes','bead kit 3mm','art things','beginner needlepoint','bead work','aquabeads big kit','ayuma playmobil','10 embroidery needles','cool maker sewing machine refills','beads iron melts','counted cross stitch','card making kit','boys cross-stitch ages 5-8','aguja magica para bordar kit','boys cross stitch kit','color aqua beads','beados tool','boho craft box kit','artkal','character fabric','bead kit','aquabeads refill pack','alice peterson','beads for pens','beads for jewelry making kids','bedos beads machine','air beads','2.6mm small fuse bead pegboard','bordado punto cruz minecraft','beads for kandi making','melting beads','cross stitch kits for beginners','hama beads kit','perler beads set and kit','seed beads for jewelry making','latchkits','stitch and zip needlepoint','perler beads bulk','melting beads for kids','latch hook kit pillow','latch rug kits for kids','micro beads','beads bulk','avengers cross stitch kits','plastic beads','anime beads','hook rug kits for kids','needlepoint kit','mini perler bead board','latch hook rug kits for kids','cross stitch kits for adults beginner funny','needlepoint kids','latch hook for kids','crafts for girls','cross stitch fabric','adult latch hook kits for kids','needles kit for 8-10','doll making kits','sewing kit for kids 4-7','locker hooking small kit','mini latch hook craft','black melting beads','dinosaur needle punch kit','perler set','plastic canvas kits for kids','punch needle small pillows','24000 fuse beads kit','melting plastic beads','knitting machine','crossstitching kits kids beginner','seed bead kit','knitting for beginners','mini felt fairies','5 mm perler beads','fuse beads pegboards','bead ironing kit','pastel bead set','latch hook loom','aqua beads refill with patterns','punch needle kit for beginners','small beads bulk','beads that melt with iron','irons for beads','needlepoint kits for kids','fuse bead boards','pillow stitching','fuse beads 5mm','pokemon perler','pillow embroidery kits for adults','mini round beads','hama beads board 2.6 mm','kids cross stitch','latchkits unicorn','hama','plastic needles for kids','aqua beads refill pack','small latch hook kit','perler bead accessories','sewing machines for kids','micro beads arts and craft','perler storage','stitch & zip','mini fuse bead patterns','pokemon cross stitch','10 in looms','christmas stocking needlepoint kits','funny embroidery kit','knitting kit for kids ages 8-12','gray perler beads','diy purse making kit','perler board for 2.6','nano beads kit','rainbow beginner yarn','small beads for waist beads making','rug hook art','art pop pencils','latch hook owl','needle point kits adults beginner','dog cross stitch kits','pixel bead kits','childrens punch needle kit','latch hook tool','play beads','embroidery purse kit','fuse beads kit for kids','disney latch hook','perler patterns','my 1st sewing','cartoon beads','kids cross stitch kit boy','crochet kit for beginners kids','bead weaving kit','pokemon beads','beginner punch needle kit','learn to knit kits for kids beginner','fused bead kit','hama beads 2.6 mm','ezee beads','sewing kit for adults','hook rug for 7 year old','needlework cloth squares','needlepoint','perler bead supplies','cross stitch starter kit for beginners','learn to sew machine kit kids','perler beads set mini','arts and crafts for kids ages 8-12','latch hook rugs owl','boys first embroidery','kid craft weaving loom','fuze beads','hook rug kits for kids for beginners','aesthetic beads kit','latch hook art','quefe beads','weaving kit','loom kit for girls','mini perler bead set','embroidery supplies','perler mini beads','panda needle box','hook rug pillow for kids','mini iron','latch hook kits for kids beginner easy','hama beads 5 mm','cross stitch beginners kit printed','bead maker kit','sew and stitch art','keychain sewing kit','small iron','star bead','loom sewing','aquabeads kids','beads tiny','water fused beads','cute crochet hooks','felt unicorn craft','stitch and zip kits','embroidery transfers','perler beads mini','little star quilt pattern','embroidery keychains','stiching','sticky beads','tri beads for crafts','small perler beads','fairy stuffed doll','shinshin mini fuse beads','food cross stitch','cat embroidery kit for beginners','mini hama bead kit','loom knitting for kids','punch needle rug kit','embroidery machine for clothing','tiny bead set','yarn pillow cases latch hook','plastic loom hooks','perler beads 5mm','small bead kit','marvel cross stitch kits','cross stitch yoshi','beginning knitting or crochet sets for girls','perler beads set glow in the dark','embroidery pillow kit for beginners','dimensions cross stitch kits','clear seed beads','mini colorful beads','crochet with needle kids','pencil case for girls','fuse bead pegboards','embroidery crafts','plastic canvas purse','send beads','needlepoint fabric','cupcake latch hook kit','hama beads 5mm','plur beads','liverpool rainbow fabric','light green perler beads','sewing machine for kids 4-7','seed beads for bracelets making','needlepoint kits for teens','mini art bead crafts','poly beads','pillow making kit for adults','melty beads','stitch n learn embroidery','perler bead board','bead loom kit','cross stitching how to kit','loom hook','perler kits for adults','cross stitch kits keychain','weaving loom kit','perler beads purple','pegboard fuse beads','glass bead bracelet kit','needlepoint pillow kits for adults','elephant cross stitch']
neg3 = set(x.lower().strip() for x in neg3_list)

all_negatives = neg1 | neg2 | neg3
neg_in_2plus = set()
for term in all_negatives:
    c = sum([term in neg1, term in neg2, term in neg3])
    if c >= 2:
        neg_in_2plus.add(term)

# Protected = any term with orders > 0 across ANY catch-all campaign
protected_terms = set()
for term, stats in all_perf.items():
    if stats['orders'] > 0:
        protected_terms.add(term)

# LIST 1: Safe to negate in campaigns 4-6
safe_to_negate = sorted(neg_in_2plus - protected_terms)

# Which of those have actual spend in 4-6?
negate_with_spend = []
for term in safe_to_negate:
    if term in unp_perf and unp_perf[term]['cost'] > 0:
        s = unp_perf[term]
        negate_with_spend.append({'term': term, 'cost': s['cost'], 'clicks': s['clicks'], 'impressions': s['impressions']})
negate_with_spend.sort(key=lambda x: x['cost'], reverse=True)
waste_total = sum(e['cost'] for e in negate_with_spend)

# LIST 2: Un-negate from campaigns 1-3
unnegate = []
for term in all_negatives:
    perf = all_perf.get(term, None)
    if perf and perf['orders'] > 0:
        acos = (perf['cost'] / perf['sales'] * 100) if perf['sales'] > 0 else float('inf')
        cvr = (perf['orders'] / perf['clicks'] * 100) if perf['clicks'] > 0 else 0
        negated_in = []
        if term in neg1: negated_in.append('Cmp1')
        if term in neg2: negated_in.append('Cmp2')
        if term in neg3: negated_in.append('Cmp3')
        perf_src = []
        if term in unp_perf and unp_perf[term]['orders'] > 0:
            perf_src.append(f"4-6:{unp_perf[term]['orders']}ord")
        if term in prot_perf and prot_perf[term]['orders'] > 0:
            perf_src.append(f"1-3:{prot_perf[term]['orders']}ord")
        unnegate.append({
            'term': term,
            'cost': perf['cost'], 'sales': perf['sales'], 'orders': perf['orders'],
            'acos': acos, 'cvr': cvr,
            'negated_in': ', '.join(negated_in),
            'perf_source': ', '.join(perf_src),
        })
unnegate.sort(key=lambda x: x['orders'], reverse=True)

# ===== OUTPUT =====
print(f'=== LIST 1: NEGATIVES TO ADD TO CAMPAIGNS 4, 5, 6 ===')
print(f'Total: {len(safe_to_negate)} terms (0 converting terms excluded)')
print(f'With actual spend in 4-6: {len(negate_with_spend)} terms, ${waste_total:.2f} waste/14d')
print()
print(f'--- Active waste (terms with spend in 4-6, zero orders anywhere) ---')
for i, e in enumerate(negate_with_spend, 1):
    print(f'{i:>3}. {e["term"]:<55} ${e["cost"]:>6.2f}  {e["clicks"]:>3}clk  {e["impressions"]:>5}imp')
print()

negate_no_spend = [t for t in safe_to_negate if t not in set(e['term'] for e in negate_with_spend)]
print(f'--- Preventive (no spend yet, {len(negate_no_spend)} terms) ---')
for i, term in enumerate(sorted(negate_no_spend), 1):
    print(f'{i:>3}. {term}')

print()
print()
print(f'=== LIST 2: UN-NEGATE FROM CAMPAIGNS 1-3 ({len(unnegate)} terms) ===')
print(f'These convert well but are blocked in campaigns 1-3.')
print()
for i, e in enumerate(unnegate, 1):
    acos_str = f'{e["acos"]:.0f}%' if e['acos'] != float('inf') else 'INF'
    print(f'{i:>3}. {e["term"]:<45} {e["orders"]:>2}ord  ${e["sales"]:>7.2f}sales  {acos_str:>5}ACoS  {e["cvr"]:>5.1f}%CVR  negated:{e["negated_in"]:<20}  from:{e["perf_source"]}')

# Save both lists as JSON for execution
output = {
    'negate_list': safe_to_negate,
    'negate_with_spend': negate_with_spend,
    'unnegate_list': [{'term': e['term'], 'negated_in': e['negated_in'], 'orders': e['orders'], 'sales': e['sales'], 'acos': round(e['acos'], 1)} for e in unnegate],
    'summary': {
        'total_negate': len(safe_to_negate),
        'negate_active_waste': f'${waste_total:.2f}/14d',
        'total_unnegate': len(unnegate),
    }
}
out_path = f'{BASE}/outputs/research/ppc-agent/portfolio-action-plan/data/2026-03-03-catch-all-auto-lists.json'
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f'\nSaved to: {out_path}')
