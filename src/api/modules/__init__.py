from api.modules.hudsonrock import HudsonRockModule
from api.modules.sherlock import SherlockModule
from api.modules.whatsmyname import WhatsMyNameModule
from api.modules.holehe import HoleheModule
from api.modules.ipinfo import IPInfoModule
from api.modules.whois_module import WhoisModule
from api.modules.subfinder import SubfinderModule
from api.modules.hibp import HibpModule
from api.modules.shodan import ShodanModule
from api.modules.hunter_io import HunterIOModule
from api.modules.virustotal import VirusTotalModule

ALL_MODULES = [
    HudsonRockModule(),
    SherlockModule(),
    WhatsMyNameModule(),
    HoleheModule(),
    IPInfoModule(),
    WhoisModule(),
    SubfinderModule(),
    HibpModule(),
    ShodanModule(),
    HunterIOModule(),
    VirusTotalModule(),
]
