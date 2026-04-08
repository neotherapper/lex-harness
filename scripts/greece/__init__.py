# scripts/greece/__init__.py
from scripts.core.registry import register
from scripts.greece.fetchers.et_gr import EtGrFetcher
from scripts.greece.fetchers.kodiko import KodikoFetcher
from scripts.greece.fetchers.gslegal import GsLegalFetcher
from scripts.greece.fetchers.hellenicparliament import HellenicParliamentFetcher
from scripts.shared.eur_lex import EurLexFetcher

register("greece", "et_gr", EtGrFetcher)
register("greece", "kodiko", KodikoFetcher)
register("greece", "gslegal", GsLegalFetcher)
register("greece", "hellenicparliament", HellenicParliamentFetcher)
register("greece", "eur_lex", EurLexFetcher)
