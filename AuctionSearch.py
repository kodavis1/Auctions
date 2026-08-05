import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
import webbrowser

# ── HIBID AUTH ────────────────────────────────────────────────
# Reads credentials from environment variables / GitHub Actions
# secrets: HIBID_USERNAME, HIBID_PASSWORD, HIBID_USER_ID
HIBID_USERNAME   = os.environ.get("HIBID_USERNAME", "")
HIBID_PASSWORD   = os.environ.get("HIBID_PASSWORD", "")
HIBID_AUTH_TOKEN = get_hibid_token(HIBID_USERNAME, HIBID_PASSWORD) if HIBID_USERNAME and HIBID_PASSWORD else ""
 
# ── EBTH AUTH ─────────────────────────────────────────────────
# Still using the manual cookie/token for now until the EBTH
# login request is confirmed (see get_ebth_session above).
# Reads from environment variables / GitHub Actions secrets:
# EBTH_API_TOKEN, EBTH_SESSION_COOKIE, EBTH_USER_ID

EBTH_API_TOKEN      = os.environ.get("7a2ab11cfe70777231c82cf4325c6e96", "")
EBTH_SESSION_COOKIE = os.environ.get("__cmpconsent98755=CQn6pwgQn6pwgAfTdBENCpFgAAAAAAAAAAigF5wBAAKgAgABUAvMC84AgAFQAQAAqAXmAAA; __cmpcccu98755=aCQn8hIYgBuS8wEWmtWMIyJiVqYSrV0A8hDILAQGoQagYAA; __cmpccpausps=1YNN; ajs_anonymous_id=379238e5-bdfa-46df-ade2-90fe9aa3cd98;", "")
EBTH_USER_ID        = os.environ.get("8191099", "")

# ══════════════════════════════════════════════════════════════
# ── SHARED KEYWORD FILTERS (used by all tabs unless overridden)
# ══════════════════════════════════════════════════════════════
INCLUDE_MATERIAL  = ["417", "925", "900", "585", "750", "10k", "10kp", "14k", "14kp", "18k", "22k"
                     , "silver", "gold", "sterling", "platinum", "solid", "SS"
                     , "diamond", "natural", "lab grown", "natural ruby", "natural emerald"
                     , "Rolex", "Longines", "Omega", "Swiss", "Pandora", "Lagos", "Francisco Zuni"
                     , "Scott Kay"
                     ]
INCLUDE_ITEM      = ["ring", "necklace", "bracelet", "pendant", "watch"
                     , "earring", "chain", "locket", "cuff", "mount", "money clip"]
INCLUDE_CONDITION = ["unmarked", "no mark", "hallmark", "marked", "missing", "broken", "repair"
                     , "worn", "stamped", "unmarked", "vintage", "antique", "condition"
                     , "grams", "wear", "estate", "tarnish", "cut", ""]

EXCLUDE_WORDS     = ["silver plate", "silverplate",  "fashion", "rhinestone"
                     , "avon", "monet", "brooch", "hatpin", "pin", "replica", "reproduction"
                     , "novelty", "faux", "inspired", "huitan", "hebrew"]
SOFT_EXCLUDE_WORDS = ["collection", "silver tone", "silver-tone", "costume", "silvertone", "plated"
                      , "gold tone", "gold-tone", "gold filled", "goldfilled", "KGF", "moissanite"
                      , "bangle", "CZ", "KGE", "KGP", "synthetic", "cufflinks", "tie clip"
                      , "lookalike", "style", "simulated", "glass", "simulant","electroform"]
SOFT_THRESHOLD    = 3

# ══════════════════════════════════════════════════════════════
# ── TAB 1: HIBID JEWELRY ──────────────────────────────────────
# ══════════════════════════════════════════════════════════════
HJ_CATEGORY_IDS       = [40254]
HJ_INCLUDE_CATS       = []
HJ_EXCLUDE_CATS       = []
HJ_EXCLUDE_CAT_STRINGS = []
HJ_EXCLUDE_AUCTIONEERS = ["Property 1 Vegas", "Simrit Collections"
                           , "Gallant Jewelry Creations", "Vivaldo F. Kosi"]
HJ_MAX_HIGH_BID       = 200
HJ_MAX_MIN_BID        = 100
HJ_SHIPPING_OFFERED   = True
HJ_CLOSE_WITHIN_HOURS = 72
HJ_MIN_PICTURES       = 0
HJ_MAX_PAGES          = 100

# ══════════════════════════════════════════════════════════════
# ── TAB 2: HIBID BRANDS ───────────────────────────────────────
# ══════════════════════════════════════════════════════════════
HB_SEARCH_TERMS       = ["David Yurman", "Georg Jensen", "King Baby", "Bathing Ape", "WNBA", "NBA", "Fear of God"
                         , "Bape", "Toga Virilis", "GoPro", "Alexander Wang", "Louis Vuitton"
                         , "Gucci", "Loewe", "Terenzi", "Birkenstock 40", "John Hardy"
                         , "Hermes", "Goyard", "Cartier", "T&Co", "Fendi", "Prada"
                         , "Vivienne Westwood", "Issey Miyake", "Yohji Yamamoto", "Longchamp"
                         , "Mansur Gavriel", "Harley Davidson", "Gucci ring", "Martens"
                         , "garmin", "bose soundlink", "tracksuit", "matching set"
                         , "Apple ipad", "Apple airpods", "mac mini"]
HB_CATEGORY_IDS       = []
HB_INCLUDE_CATS       = []
HB_EXCLUDE_CATS       = [40280, 40297, 40171, 40291, 40385, 40093, 40143, 700003, 40102]
HB_EXCLUDE_CAT_STRINGS = ["Sports Cards", "Trading Cards", "Collectibles", "Comics"
                           , "Toys", "Memorabilia", "Coins", "Stamps", "Militaria"
                           , "Video Games", "Kitchen / Housewares", ""]
HB_EXCLUDE_AUCTIONEERS = ["Property 1 Vegas", "Simrit Collections"
                           , "Gallant Jewelry Creations", "Vivaldo F. Kosi"]
HB_EXCLUDE_WORDS      = ["battery", "charger", "ipad case", "ink cartridge", "adapter"
                         , "printer", "holder", "cleaning", "case for ipad", "speaker system"
                         , "untested", "not working", "for parts only", "Charging Cable"
                         , "inspired", "style", "off-brand", "not authenticated", "damaged"
                         , "trading card", "baseball card", "sports card", "football card"
                         , "basketball card", "topps", "panini", "upper deck", "rookie card"
                         , "memorabilia card", "comic", "funko", "pop vinyl", "action figure"
                         , "beanie baby", "gps", "huitan"]
HB_MAX_HIGH_BID       = 500
HB_MAX_MIN_BID        = 200
HB_SHIPPING_OFFERED   = True
HB_CLOSE_WITHIN_HOURS = 72
HB_MAX_PAGES          = 100

# ══════════════════════════════════════════════════════════════
# ── TAB 3: EBTH ───────────────────────────────────────────────
# Pass one or more path slugs. Each is fetched separately and
# merged into a single "EBTH" section.
# Common slugs:
#   /jewelry-and-watches
#   /fashion-and-accessories
#   /collectibles
# Leave empty to fetch all categories (no path filter).
# ══════════════════════════════════════════════════════════════
EJ_PATH_SLUGS         = ["/jewelry-and-watches",
                         "/fashion-and-accessories",
                         "/art/paintings-and-drawings",   # acrylic, oil, watercolor, mixed media, drawings
                         "/art/prints",
                         "/electronics-and-computers/computers"]
EJ_EXCLUDE_WORDS      = ["electroform", "pendant earring", "pop art"]
EJ_MAX_HIGH_BID       = 200
EJ_MAX_MIN_BID        = 100
EJ_SHIPPING_ONLY      = True
EJ_CLOSE_WITHIN_HOURS = 48
EJ_MAX_PAGES          = 300


# ══════════════════════════════════════════════════════════════
# ── HIBID HEADERS ─────────────────────────────────────────────
hibid_url = "https://hibid.com/graphql"

def hibid_headers():
    h = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://hibid.com",
        "Referer": "https://hibid.com/lots?q=unmarked&status=OPEN"
    }
    if HIBID_AUTH_TOKEN:
        h["Authorization"] = f"Bearer {HIBID_AUTH_TOKEN}"
    return h

# ── EBTH HEADERS ──────────────────────────────────────────────
ebth_url = "https://www.ebth.com/api/v1/twosearch/items"

def ebth_headers():
    h = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/json",
        "Referer": "https://www.ebth.com/jewelry-and-watches",
        "X-Requested-With": "XM20.LHttpRequest",
    }
    if EBTH_API_TOKEN:
        h["Authorization"] = f"Token token={EBTH_API_TOKEN}"
    return h

# ══════════════════════════════════════════════════════════════
# ── GRAPHQL QUERIES ───────────────────────────────────────────

HIBID_CATEGORY_QUERY = """query CategoryList($flatCategories: Boolean = false) {
  categoryTree(input: {allCategories: true, flatCategories: $flatCategories}) {
    id
    categoryName
    fullCategory
    children {
      id
      categoryName
      fullCategory
      children {
        id
        categoryName
        fullCategory
        children {
          id
          categoryName
          fullCategory
        }
      }
    }
  }
}"""

HIBID_LOT_QUERY = """query LotSearch($pageNumber: Int!, $pageLength: Int!, $searchText: String = null, $category: CategoryId = null, $status: AuctionLotStatus = null, $filter: AuctionLotFilter = null, $shippingOffered: Boolean = false, $countryName: String = null) {
  lotSearch(
    input: {searchText: $searchText, status: $status, filter: $filter, category: $category, shippingOffered: $shippingOffered, countryName: $countryName}
    pageNumber: $pageNumber
    pageLength: $pageLength
    sortDirection: DESC
  ) {
    pagedResults {
      pageLength
      pageNumber
      totalCount
      results {
        id
        lead
        lotNumber
        description
        estimate
        quantity
        pictureCount
        shippingOffered
        featuredPicture {
          thumbnailLocation
          hdThumbnailLocation
        }
        pictures {
          hdThumbnailLocation
          thumbnailLocation
        }
        category {
          id
          fullCategory
        }
        lotState {
          minBid
          highBid
          bidCount
          timeLeft
          timeLeftSeconds
          reserveSatisfied
          sealed
          isClosed
        }
        auction {
          bidCloseDateTime
          eventCity
          eventState
          currencyAbbreviation
          buyerPremium
          buyerPremiumRate
          shippingAndPickupInfo
          paymentInfo
          auctioneer { name }
        }
      }
    }
  }
}"""

HIBID_WATCHLIST_QUERY = """query WatchListSearch($isArchived: Boolean = false, $groupByAuction: Boolean = true, $auctionSortDirection: SortDirection = ASC, $hideClosedLots: Boolean = false, $pageNumber: Int!, $pageLength: Int!, $auctionId: Int = null, $buyerLotStatusGroup: BuyerLotStatusGroup = null, $sortOrder: BuyerEventItemSortOrder = null, $monthRange: AltBidPastBidsRange = null, $sortDirection: SortDirection = DESC) {
  watchList(
    input: {isArchived: $isArchived, groupByAuction: $groupByAuction, auctionSortDirection: $auctionSortDirection, hideClosedLots: $hideClosedLots, auctionId: $auctionId, buyerLotStatusGroup: $buyerLotStatusGroup, sortOrder: $sortOrder, monthRange: $monthRange}
    pageNumber: $pageNumber
    pageLength: $pageLength
    sortDirection: $sortDirection
  ) {
    pagedResults {
      pageLength
      pageNumber
      totalCount
      results {
        id
        lead
        description
        estimate
        pictureCount
        pictures {
          hdThumbnailLocation
          thumbnailLocation
        }
        featuredPicture {
          hdThumbnailLocation
          thumbnailLocation
        }
        category {
          id
          fullCategory
        }
        lotState {
          bidCount
          bidMax
          buyerBidStatus
          buyerHighBid
          highBid
          isClosed
          isWatching
          minBid
          reserveSatisfied
          sealed
          timeLeft
          timeLeftSeconds
        }
        auction {
          bidCloseDateTime
          buyerPremium
          buyerPremiumRate
          currencyAbbreviation
          eventCity
          eventState
          paymentInfo
          shippingAndPickupInfo
          auctioneer { name }
        }
      }
    }
  }
}"""


# ══════════════════════════════════════════════════════════════
# ── HELPERS ───────────────────────────────────────────────────

def count_include_matches(combined, groups):
    return sum(1 for g in groups for w in g if w in combined)

def passes_include_groups(combined, groups):
    return all(not g or any(w in combined for w in g) for g in groups)

def flatten_hibid_categories(nodes, depth=0):
    rows = []
    for n in nodes:
        rows.append({"id": n["id"], "name": n["categoryName"], "full": n["fullCategory"], "depth": depth})
        for child in n.get("children") or []:
            rows.extend(flatten_hibid_categories([child], depth + 1))
    return rows

def fetch_hibid_categories(search=None):
    r = requests.post(hibid_url, headers=hibid_headers(), json={
        "operationName": "CategoryList",
        "query": HIBID_CATEGORY_QUERY,
        "variables": {"flatCategories": False}
    })
    nodes = r.json()["data"]["categoryTree"]
    df = pd.DataFrame(flatten_hibid_categories(nodes))
    if search:
        df = df[df["full"].str.contains(search, case=False)]
    print(df.to_string(index=False))
    return df

def dedup_lots(lots):
    seen = {}
    for lot in lots:
        lot_id = lot["id"]
        if lot_id not in seen or (seen[lot_id]["bid_status"] is None and lot["bid_status"] is not None):
            seen[lot_id] = lot
    return list(seen.values())


# ══════════════════════════════════════════════════════════════
# ── HIBID WATCHLIST FETCH ─────────────────────────────────────

def fetch_hibid_account_lots():
    if not HIBID_AUTH_TOKEN:
        return set(), {}

    watchlist_ids = set()
    bid_info      = {}
    page = 1

    while True:
        try:
            r = requests.post(hibid_url, headers=hibid_headers(), json={
                "operationName": "WatchListSearch",
                "query": HIBID_WATCHLIST_QUERY,
                "variables": {
                    "isArchived": False,
                    "groupByAuction": False,
                    "auctionSortDirection": "ASC",
                    "hideClosedLots": True,
                    "pageNumber": page,
                    "pageLength": 100,
                    "auctionId": 0,
                    "buyerLotStatusGroup": "ALL",
                    "sortOrder": "SALES_ORDER",
                    "monthRange": "THREE_MONTHS",
                    "sortDirection": "ASC"
                }
            }, timeout=15)
            data = r.json()

            if "errors" in data:
                print(f"  HiBid watchlist error: {data['errors']}")
                break

            paged   = data["data"]["watchList"]["pagedResults"]
            results = paged.get("results") or []
            total   = paged.get("totalCount") or 0

            if not results:
                break

            for lot in results:
                lot_id       = str(lot["id"])
                lot_state    = lot.get("lotState") or {}
                buyer_status = lot_state.get("buyerBidStatus") or ""
                my_max_bid   = lot_state.get("bidMax") or 0
                my_high_bid  = lot_state.get("buyerHighBid") or 0

                watchlist_ids.add(lot_id)

                if buyer_status and buyer_status != "NO_BID":
                    status = ("winning" if buyer_status == "HIGH_BIDDER"
                              else "outbid" if buyer_status == "OUTBID"
                              else "bidding")
                    bid_info[lot_id] = {"status": status, "my_bid": my_max_bid, "my_high_bid": my_high_bid}

            print(f"  HiBid watchlist page {page}: {len(results)} lots (total {total})")
            if page * 100 >= total:
                break
            page += 1

        except Exception as e:
            print(f"  HiBid watchlist fetch error: {e}")
            break

    winning = sum(1 for v in bid_info.values() if v["status"] == "winning")
    outbid  = sum(1 for v in bid_info.values() if v["status"] == "outbid")
    print(f"  HiBid account: {len(watchlist_ids)} watched, {winning} winning, {outbid} outbid")
    return watchlist_ids, bid_info


# ══════════════════════════════════════════════════════════════
# ── HIBID FETCH ───────────────────────────────────────────────

def fetch_hibid_lots(category_id, cfg, search_override=None, cutoff_dt=None,
                     watchlist_ids=None, bid_status=None):
    all_results      = []
    page             = 1
    include_groups   = [g for g in [INCLUDE_MATERIAL, INCLUDE_ITEM, INCLUDE_CONDITION] if g]
    include_cats     = cfg.get("include_cats", [])
    exclude_cats     = cfg.get("exclude_cats", [])
    exclude_cat_strs = cfg.get("exclude_cat_strings", [])
    excl_aucti       = cfg.get("exclude_auctioneers", [])
    excl_words       = cfg.get("exclude_words", [])
    max_high_bid     = cfg.get("max_high_bid")
    max_min_bid      = cfg.get("max_min_bid")
    shipping         = cfg.get("shipping_offered", False)
    min_pics         = cfg.get("min_pictures", 0)
    max_pages        = cfg.get("max_pages", 100)
    use_jewel_filter = cfg.get("use_jewelry_filters", False)
    search_text      = search_override or ""

    while page <= max_pages:
        try:
            r = requests.post(hibid_url, headers=hibid_headers(), json={
                "operationName": "LotSearch",
                "query": HIBID_LOT_QUERY,
                "variables": {
                    "pageNumber": page,
                    "pageLength": 100,
                    "searchText": search_text or None,
                    "status": "OPEN",
                    "filter": "ALL",
                    "category": category_id,
                    "shippingOffered": shipping,
                    "countryName": "United States"
                }
            }, timeout=15)
            content_type = r.headers.get("Content-Type", "")
            if r.status_code != 200 or "application/json" not in content_type:
                print(f"  HiBid page {page} skipped (status {r.status_code}, content-type: {content_type.split(';')[0].strip()})")
                print(f"  HiBid response body[:200]: {r.text[:200]!r}")
                break
            data = r.json()
        except Exception as e:
            print(f"  HiBid page {page} error: {e}")
            break

        paged   = data["data"]["lotSearch"]["pagedResults"]
        results = paged["results"]
        total   = paged["totalCount"]

        if not results:
            break

        for lot in results:
            title      = (lot.get("lead") or "").lower()
            desc       = (lot.get("description") or "").lower()
            combined   = title + " " + desc
            auctioneer = (lot["auction"]["auctioneer"].get("name") or "").lower()
            high_bid   = lot["lotState"].get("highBid") or 0
            min_bid    = lot["lotState"].get("minBid") or 0
            currency   = lot["auction"].get("currencyAbbreviation", "USD")
            pic_count  = lot.get("pictureCount") or 0
            sealed     = lot["lotState"].get("sealed") or False

            raw_cat    = lot.get("category")
            if isinstance(raw_cat, list):
                raw_cat = raw_cat[0] if raw_cat else {}
            raw_cat        = raw_cat or {}
            lot_cat_id     = raw_cat.get("id")
            lot_cat        = raw_cat.get("fullCategory") or ""
            try:
                lot_cat_id_int = int(lot_cat_id) if lot_cat_id is not None else None
            except (ValueError, TypeError):
                lot_cat_id_int = None

            if cutoff_dt:
                raw_close = lot["auction"].get("bidCloseDateTime")
                if not raw_close:
                    continue
                try:
                    close_dt = datetime.fromisoformat(raw_close.replace("Z", "+00:00"))
                    if close_dt.tzinfo is None:
                        close_dt = close_dt.replace(tzinfo=timezone.utc)
                    if close_dt > cutoff_dt:
                        continue
                except Exception as e:
                    print(f"  HiBid unparseable date '{raw_close}': {e}")
                    continue

            if include_cats and lot_cat_id_int not in include_cats:
                continue
            if exclude_cats and lot_cat_id_int in exclude_cats:
                continue
            if exclude_cat_strs and any(s.lower() in lot_cat.lower() for s in exclude_cat_strs):
                continue
            if any(w.lower() in combined for w in EXCLUDE_WORDS):
                continue
            if excl_words and any(w.lower() in combined for w in excl_words):
                continue
            if excl_aucti and any(a.lower() in auctioneer for a in excl_aucti):
                continue
            if currency != "USD":
                continue
            if max_high_bid is not None and not sealed and high_bid > max_high_bid:
                continue
            if max_min_bid is not None and min_bid > max_min_bid:
                continue
            if use_jewel_filter:
                if not passes_include_groups(combined, include_groups):
                    continue
                if any(w.lower() in combined for w in SOFT_EXCLUDE_WORDS):
                    if count_include_matches(combined, include_groups) < SOFT_THRESHOLD:
                        continue
            if pic_count < min_pics:
                continue

            fp         = lot.get("featuredPicture") or {}
            auction    = lot["auction"]
            lot_state  = lot["lotState"]
            lot_id_str = str(lot["id"])

            is_watched  = bool(watchlist_ids and lot_id_str in watchlist_ids)
            lot_bid     = bid_status.get(lot_id_str) if bid_status else None
            bid_stat    = lot_bid["status"]      if lot_bid else None
            my_bid      = lot_bid["my_bid"]      if lot_bid else None
            my_high_bid = lot_bid["my_high_bid"] if lot_bid else None

            all_results.append({
                "id":            lot["id"],
                "title":         lot.get("lead") or "",
                "pictures":      [p.get("hdThumbnailLocation") or p.get("thumbnailLocation")
                                  for p in (lot.get("pictures") or [])
                                  if p.get("hdThumbnailLocation") or p.get("thumbnailLocation")]
                                 or ([fp.get("hdThumbnailLocation") or fp.get("thumbnailLocation")]
                                     if fp.get("hdThumbnailLocation") or fp.get("thumbnailLocation") else []),
                "pic_count":     pic_count,
                "min_bid":       min_bid,
                "high_bid":      high_bid,
                "sealed":        sealed,
                "bid_count":     lot_state.get("bidCount") or 0,
                "reserve_met":   lot_state.get("reserveSatisfied"),
                "time_left":     lot_state.get("timeLeft") or "",
                "estimate":      lot.get("estimate") or "",
                "buyer_premium": auction.get("buyerPremium") or "",
                "closes":        auction.get("bidCloseDateTime") or "",
                "location":      f"{auction.get('eventCity','')}, {auction.get('eventState','')}".strip(", "),
                "seller":        auction["auctioneer"].get("name") or "",
                "category":      lot_cat,
                "description":   lot.get("description") or "",
                "shipping_info": auction.get("shippingAndPickupInfo") or "",
                "payment_info":  auction.get("paymentInfo") or "",
                "certified":     False,
                "condition":     "",
                "url":           f"https://hibid.com/lot/{lot['id']}",
                "source":        "HiBid",
                "watched":       is_watched,
                "bid_status":    bid_stat,
                "my_bid":        my_bid,
                "my_high_bid":   my_high_bid,
                "followed_status": None,
            })

        print(f"  Page {page}: {len(results)} fetched, {total} total")
        if page * 100 >= total:
            break
        page += 1

    return all_results


# ══════════════════════════════════════════════════════════════
# ── EBTH FOLLOWED ITEMS ───────────────────────────────────────

def fetch_ebth_followed_ids():
    if not EBTH_SESSION_COOKIE:
        return {}
    try:
        r = requests.get(
            "https://www.ebth.com/users/followed_items",
            headers={
                **ebth_headers(),
                "Accept": "text/html,application/xhtml+xml",
                "Cookie": EBTH_SESSION_COOKIE
            },
            timeout=15
        )
        import re
        followed = {}
        for match in re.finditer(r'id="item_(\d+)"[^>]*class="[^"]*table-followed-items__item--(\w+)[^"]*followed-items-desktop', r.text):
            item_id = str(match.group(1))
            status_class = match.group(2)
            followed[item_id] = 'outbid' if status_class == 'outbid' else 'following'
        print(f"  EBTH: {len(followed)} followed items loaded")
        return followed
    except Exception as e:
        print(f"  EBTH followed items error: {e}")
        return {}


# ══════════════════════════════════════════════════════════════
# ── EBTH FETCH ────────────────────────────────────────────────

def fetch_ebth_lots(path_slug, cfg, search_override=None, cutoff_dt=None):
    """
    path_slug: e.g. '/jewelry-and-watches', or None for no filter.
    cfg keys: exclude_words, max_high_bid, max_min_bid, shipping_only,
              max_pages, use_jewelry_filters (bool)
    """
    all_results      = []
    page             = 1
    include_groups   = [g for g in [INCLUDE_MATERIAL, INCLUDE_ITEM, INCLUDE_CONDITION] if g]
    excl_words       = cfg.get("exclude_words", [])
    max_high_bid     = cfg.get("max_high_bid")
    max_min_bid      = cfg.get("max_min_bid")
    shipping_only    = cfg.get("shipping_only", False)
    max_pages        = cfg.get("max_pages", 100)
    use_jewel_filter = cfg.get("use_jewelry_filters", False)

    while page <= max_pages:
        params = {"page": page, "per_page": 48, "sort": "sale_ends_at_asc"}
        if path_slug is not None:
            params["path"] = path_slug
        if search_override:
            params["q"] = search_override
        if shipping_only:
            params["shipping"] = "true"

        try:
            r = requests.get(ebth_url, headers=ebth_headers(), params=params, timeout=15)
            content_type = r.headers.get("Content-Type", "")
            if r.status_code != 200 or "application/json" not in content_type:
                print(f"  EBTH path={path_slug} page {page} skipped (status {r.status_code}, content-type: {content_type.split(';')[0].strip()})")
                print(f"  EBTH response body[:200]: {r.text[:200]!r}")
                break
            data = r.json()
        except Exception as e:
            print(f"  EBTH path={path_slug} page {page} error: {e}")
            break

        items       = data.get("items") or []
        pagination  = data.get("pages") or {}
        total_pages = pagination.get("total_pages") or 1

        if not items:
            break

        for item in items:
            title    = (item.get("name") or "").lower()
            desc     = (item.get("condition_details") or "").lower()
            combined = title + " " + desc
            high_bid = item.get("high_bid_amount") or 0
            min_bid  = item.get("minimum_bid_amount") or 0

            if cutoff_dt:
                raw_close = item.get("sale_ends_at")
                if not raw_close:
                    continue
                try:
                    close_dt = datetime.fromisoformat(raw_close.replace("Z", "+00:00"))
                    if close_dt.tzinfo is None:
                        close_dt = close_dt.replace(tzinfo=timezone.utc)
                    if close_dt > cutoff_dt:
                        continue
                except Exception as e:
                    print(f"  EBTH unparseable date '{raw_close}': {e}")
                    continue

            if any(w.lower() in combined for w in EXCLUDE_WORDS):
                continue
            if excl_words and any(w.lower() in combined for w in excl_words):
                continue
            if max_high_bid is not None and high_bid > max_high_bid:
                continue
            if max_min_bid is not None and min_bid > max_min_bid:
                continue
            if use_jewel_filter:
                if not any(w in combined for w in INCLUDE_MATERIAL) and not any(w in combined for w in INCLUDE_ITEM):
                    continue
                if any(w.lower() in combined for w in SOFT_EXCLUDE_WORDS):
                    if count_include_matches(combined, include_groups) < SOFT_THRESHOLD:
                        continue

            all_results.append({
                "id":            item["id"],
                "title":         item.get("name") or "",
                "pictures":      item.get("images") or [],
                "pic_count":     len(item.get("images") or []),
                "min_bid":       min_bid,
                "high_bid":      high_bid,
                "sealed":        False,
                "bid_count":     item.get("bids_count") or 0,
                "reserve_met":   None,
                "time_left":     "",
                "estimate":      "",
                "buyer_premium": "",
                "closes":        item.get("sale_ends_at") or "",
                "location":      item.get("pickup_city_state") or "",
                "seller":        "",
                "category":      "",
                "description":   item.get("condition_details") or "",
                "shipping_info": "",
                "payment_info":  "",
                "certified":     bool(item.get("certified_authentic")),
                "condition":     item.get("condition_details") or "",
                "url":           f"https://www.ebth.com{item.get('public_url','')}",
                "source":        "EBTH",
                "watched":       False,
                "bid_status":    None,
                "my_bid":        None,
                "my_high_bid":   None,
                "followed_status": None,
            })

        print(f"  EBTH path={path_slug} page {page}/{total_pages}: {len(items)} fetched")
        if page >= total_pages:
            break
        page += 1

    return all_results


# ══════════════════════════════════════════════════════════════
# ── HTML GENERATION ───────────────────────────────────────────

def generate_html(hibid_jewelry, hibid_brands, ebth_lots, output_path, run_time):
    def lot_card(lot):
        sealed_badge    = '<span class="badge sealed">SEALED</span>' if lot["sealed"] else ""
        certified_badge = '<span class="badge certified">Certified Authentic</span>' if lot.get("certified") else ""

        bid_stat    = lot.get("bid_status")
        my_bid      = lot.get("my_bid")
        my_high_bid = lot.get("my_high_bid")

        if bid_stat == "winning":
            bid_badge = '<span class="badge winning">Winning</span>'
        elif bid_stat == "outbid":
            bid_badge = '<span class="badge outbid">Outbid</span>'
        elif bid_stat == "bidding":
            bid_badge = '<span class="badge bidding">Bidding</span>'
        else:
            bid_badge = ""

        my_bid_row = ""
        if my_bid:
            my_high_str = (f" &nbsp;|&nbsp; <span class='bid-label'>Your high:</span>"
                           f" <span class='bid-val my-bid'>${my_high_bid:,.2f}</span>") if my_high_bid else ""
            my_bid_row = (f'<div class="bid-row my-bid-row">'
                          f'<span class="bid-label">Your max:</span>'
                          f' <span class="bid-val my-bid">${my_bid:,.2f}</span>{my_high_str}</div>')

        if lot.get("watched") and not bid_stat:
            watch_badge = '<span class="badge watching">Saved</span>'
        elif lot.get("followed_status") == "outbid":
            watch_badge = '<span class="badge outbid">Outbid</span>'
        elif lot.get("followed_status") == "following":
            watch_badge = '<span class="badge following">Following</span>'
        else:
            watch_badge = ""

        reserve = ""
        if lot["reserve_met"] is True:
            reserve = '<span class="badge reserve-met">Reserve Met</span>'
        elif lot["reserve_met"] is False:
            reserve = '<span class="badge reserve-not">Reserve Not Met</span>'

        high_bid_display = "SEALED" if lot["sealed"] else (f'${lot["high_bid"]:,.2f}' if lot["high_bid"] else "No bids")
        estimate      = f'<div class="meta">Estimate: {lot["estimate"]}</div>' if lot.get("estimate") else ""
        premium       = f'<div class="meta">Buyer\'s Premium: {lot["buyer_premium"]}</div>' if lot.get("buyer_premium") else ""
        category      = f'<div class="meta">Category: {lot["category"]}</div>' if lot.get("category") else ""
        seller_line   = f'<div class="meta">{lot["seller"]} &mdash; ' if lot.get("seller") else '<div class="meta">'
        description   = f'<div class="note-row"><span class="note-label">Description:</span> {lot["description"]}</div>' if lot.get("description") else ""
        shipping_info = f'<div class="note-row"><span class="note-label">Shipping:</span> {lot["shipping_info"]}</div>' if lot.get("shipping_info") else ""
        payment_info  = f'<div class="note-row"><span class="note-label">Payment:</span> {lot["payment_info"]}</div>' if lot.get("payment_info") else ""

        closes = ""
        if lot["closes"]:
            try:
                dt = datetime.fromisoformat(lot["closes"].replace("Z", "+00:00"))
                closes = dt.strftime("%b %d, %Y %I:%M %p")
            except:
                closes = lot["closes"]

        time_left_str = f" &nbsp;|&nbsp; Time Left: {lot['time_left']}" if lot.get("time_left") else ""
        pics = lot.get("pictures") or []
        photo_html = "".join(
            f'<img src="{p}" onerror="this.style.display=\'none\'">' for p in pics
        ) if pics else '<div class="no-pic">No Photo</div>'

        source_badge = f'<span class="badge source-{lot["source"].lower()}">{lot["source"]}</span>'

        card_class = "card"
        if bid_stat == "outbid" or lot.get("followed_status") == "outbid":
            card_class = "card card-outbid"
        elif bid_stat == "winning":
            card_class = "card card-winning"
        elif bid_stat == "bidding" or lot.get("watched") or lot.get("followed_status") == "following":
            card_class = "card card-watched"

        lot_id_attr = f"{lot['source'].lower()}-{lot['id']}"
        return f"""
        <div class="{card_class}" data-lot-id="{lot_id_attr}">
          <button class="dismiss-btn" onclick="dismissLot('{lot_id_attr}')" title="Not interested">✕</button>
          <a class="card-link" href="{lot['url']}" target="_blank">
          <div class="card-photos">{photo_html}</div>
          <div class="card-body">
            <div class="card-title">{lot['title']} {sealed_badge} {certified_badge}</div>
            <div class="badges">{source_badge}{bid_badge}{watch_badge}{reserve}</div>
            <div class="bid-row">
              <span class="bid-label">Current:</span>
              <span class="bid-val">{high_bid_display}</span>
              <span class="bid-label">Min Bid:</span>
              <span class="bid-val">${lot['min_bid']:,.2f}</span>
              <span class="bid-label">Bids:</span>
              <span class="bid-val">{lot['bid_count']}</span>
            </div>
            {my_bid_row}
            {estimate}
            {premium}
            <div class="meta">Closes: {closes}{time_left_str}</div>
            {seller_line}{lot['location']} &nbsp;|&nbsp; {lot['pic_count']} photo(s)</div>
            {category}
            {description}
            {shipping_info}
            {payment_info}
          </div>
          </a>
        </div>"""

    def section(section_id, title, lots):
        if not lots:
            return f"<section id='{section_id}'><h2>{title}</h2><p>No results.</p></section>"
        cards = "\n".join(lot_card(l) for l in lots)
        return f"<section id='{section_id}'><h2>{title} <span class='count'>({len(lots)})</span></h2>{cards}</section>"

    hj = sorted(hibid_jewelry, key=lambda x: x["closes"] or "")
    hb = sorted(hibid_brands,  key=lambda x: x["closes"] or "")
    ej = sorted(ebth_lots,     key=lambda x: x["closes"] or "")
    generated = run_time.strftime("%b %d, %Y %I:%M %p")

    hj_saved = sum(1 for l in hj if l.get("watched") or l.get("bid_status"))
    hb_saved = sum(1 for l in hb if l.get("watched") or l.get("bid_status"))
    ej_saved = sum(1 for l in ej if l.get("followed_status") or l.get("bid_status"))

    auth_note = " &nbsp;|&nbsp; HiBid: authenticated" if HIBID_AUTH_TOKEN else " &nbsp;|&nbsp; HiBid: not authenticated"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Auction Results — {generated}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #111; color: #e0e0e0; padding: 20px; }}
  h1 {{ font-size: 1.4rem; margin-bottom: 4px; color: #fff; }}
  .generated {{ font-size: 0.75rem; color: #666; margin-bottom: 12px; }}
  .nav {{ margin-bottom: 20px; display: flex; gap: 16px; flex-wrap: wrap; }}
  .nav a {{ color: #c8f; font-size: 0.9rem; text-decoration: none; }}
  .nav a:hover {{ text-decoration: underline; }}
  .nav .saved-count {{ color: #f0a500; font-size: 0.75rem; margin-left: 2px; }}
  .search-bar {{ width: 100%; padding: 10px 14px; font-size: 1rem; background: #1e1e1e; border: 1px solid #333; border-radius: 6px; color: #e0e0e0; margin-bottom: 16px; }}
  .filter-row {{ display: flex; gap: 10px; margin-bottom: 24px; flex-wrap: wrap; }}
  .filter-btn {{ padding: 6px 14px; font-size: 0.8rem; background: #1e1e1e; border: 1px solid #333; border-radius: 20px; color: #aaa; cursor: pointer; transition: all 0.15s; }}
  .filter-btn:hover, .filter-btn.active {{ background: #2a2a3a; border-color: #c8f; color: #c8f; }}
  section {{ margin-bottom: 40px; }}
  h2 {{ font-size: 1.1rem; color: #aaa; border-bottom: 1px solid #222; padding-bottom: 8px; margin-bottom: 16px; }}
  .count {{ color: #555; font-weight: normal; }}
  .card {{ display: flex; flex-direction: column; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; margin-bottom: 12px; padding: 14px; color: inherit; transition: border-color 0.15s; position: relative; }}
  .card:hover {{ border-color: #555; }}
  .card-link {{ text-decoration: none; color: inherit; display: flex; flex-direction: column; }}
  .dismiss-btn {{ position: absolute; top: 8px; right: 8px; background: none; border: 1px solid #333; border-radius: 4px; color: #555; font-size: 0.7rem; padding: 2px 6px; cursor: pointer; z-index: 10; line-height: 1.4; transition: all 0.15s; }}
  .dismiss-btn:hover {{ background: #2e0e0e; border-color: #e57373; color: #e57373; }}
  .card-watched {{ border-left: 3px solid #f0a500 !important; }}
  .card-winning {{ border-left: 3px solid #4caf50 !important; }}
  .card-outbid  {{ border-left: 3px solid #e57373 !important; }}
  .card-photos {{ display: flex; gap: 8px; overflow-x: auto; margin-bottom: 12px; padding-bottom: 4px; }}
  .card-photos img {{ height: 140px; width: auto; flex-shrink: 0; border-radius: 4px; object-fit: cover; }}
  .no-pic {{ font-size: 0.7rem; color: #444; text-align: center; padding: 20px 0; }}
  .card-body {{ flex: 1; display: flex; flex-direction: column; gap: 6px; }}
  .card-title {{ font-size: 0.95rem; font-weight: 600; color: #fff; line-height: 1.3; }}
  .badges {{ display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 2px; }}
  .badge {{ font-size: 0.65rem; padding: 2px 7px; border-radius: 4px; font-weight: 600; text-transform: uppercase; }}
  .sealed {{ background: #3a2a00; color: #f0a500; }}
  .certified {{ background: #002a3a; color: #50c8f0; }}
  .reserve-met {{ background: #0e2e0e; color: #4caf50; }}
  .reserve-not {{ background: #2e0e0e; color: #e57373; }}
  .source-hibid {{ background: #1a1a3a; color: #88aaff; }}
  .source-ebth {{ background: #1a2a1a; color: #88cc88; }}
  .winning {{ background: #0e2e0e; color: #4caf50; }}
  .bidding {{ background: #2a2200; color: #f0a500; }}
  .outbid  {{ background: #2e0e0e; color: #ff6b6b; }}
  .watching, .following {{ background: #2a2200; color: #f0a500; }}
  .my-bid  {{ color: #ffd700 !important; }}
  .my-bid-row {{ margin-top: 2px; }}
  .bid-row {{ display: flex; gap: 12px; align-items: baseline; flex-wrap: wrap; }}
  .bid-label {{ font-size: 0.72rem; color: #666; }}
  .bid-val {{ font-size: 0.9rem; color: #c8f; font-weight: 600; }}
  .meta {{ font-size: 0.75rem; color: #666; }}
  .note-row {{ font-size: 0.72rem; color: #555; padding-top: 4px; }}
  .note-label {{ color: #444; font-weight: 600; text-transform: uppercase; font-size: 0.65rem; }}
  .hidden {{ display: none !important; }}
</style>
</head>
<body>
<h1>Auction Results</h1>
<div class="generated">Generated {generated}{auth_note}</div>
<div class="nav">
  <a href="#hibid-jewelry">HiBid Jewelry ({len(hj)}){f'<span class="saved-count">★{hj_saved}</span>' if hj_saved else ''}</a>
  <a href="#hibid-brands">HiBid Brands ({len(hb)}){f'<span class="saved-count">★{hb_saved}</span>' if hb_saved else ''}</a>
  <a href="#ebth">EBTH ({len(ej)}){f'<span class="saved-count">★{ej_saved}</span>' if ej_saved else ''}</a>
</div>
<input class="search-bar" type="text" placeholder="Filter results..." id="filter">
<div class="filter-row">
  <button class="filter-btn active" data-filter="all">All</button>
  <button class="filter-btn" data-filter="saved">Saved</button>
  <button class="filter-btn" data-filter="winning">Winning</button>
  <button class="filter-btn" data-filter="outbid">Outbid</button>
  <button class="filter-btn" id="toggle-dismissed">Show dismissed</button>
  <button class="filter-btn" id="clear-dismissed">Clear dismissed</button>
</div>
{section("hibid-jewelry", "HiBid Jewelry", hj)}
{section("hibid-brands", "HiBid Brands", hb)}
{section("ebth", "EBTH", ej)}
<script>
  const DISMISSED_KEY = 'hb_dismissed';

  function getDismissed() {{
    try {{ return new Set(JSON.parse(localStorage.getItem(DISMISSED_KEY) || '[]')); }}
    catch {{ return new Set(); }}
  }}

  function saveDismissed(set) {{
    localStorage.setItem(DISMISSED_KEY, JSON.stringify([...set]));
  }}

  function dismissLot(lotId) {{
    event.preventDefault();
    event.stopPropagation();
    const dismissed = getDismissed();
    dismissed.add(lotId);
    saveDismissed(dismissed);
    const card = document.querySelector(`[data-lot-id="${{lotId}}"]`);
    if (card) card.classList.add('hidden');
  }}

  let showingDismissed = false;

  function applyDismissed() {{
    const dismissed = getDismissed();
    dismissed.forEach(lotId => {{
      const card = document.querySelector(`[data-lot-id="${{lotId}}"]`);
      if (card && !showingDismissed) card.classList.add('hidden');
    }});
  }}

  document.getElementById('toggle-dismissed').addEventListener('click', function() {{
    showingDismissed = !showingDismissed;
    this.textContent = showingDismissed ? 'Hide dismissed' : 'Show dismissed';
    this.classList.toggle('active', showingDismissed);
    applyFilters();
  }});

  document.getElementById('clear-dismissed').addEventListener('click', function() {{
    if (!confirm('Clear all dismissed lots?')) return;
    saveDismissed(new Set());
    showingDismissed = false;
    document.getElementById('toggle-dismissed').textContent = 'Show dismissed';
    document.getElementById('toggle-dismissed').classList.remove('active');
    applyFilters();
  }});

  function applyFilters() {{
    const q = document.getElementById('filter').value.toLowerCase();
    const f = document.querySelector('.filter-btn.active')?.dataset.filter || 'all';
    const dismissed = getDismissed();
    document.querySelectorAll('.card').forEach(card => {{
      const isDismissed = dismissed.has(card.dataset.lotId);
      if (isDismissed && !showingDismissed) {{ card.classList.add('hidden'); return; }}
      const textMatch = !q || card.textContent.toLowerCase().includes(q);
      const filterMatch = filterCard(card, f);
      card.classList.toggle('hidden', !(textMatch && filterMatch));
    }});
  }}

  document.getElementById('filter').addEventListener('input', applyFilters);

  function filterCard(card, f) {{
    if (f === 'all')     return true;
    if (f === 'saved')   return card.classList.contains('card-watched') || card.classList.contains('card-winning') || card.classList.contains('card-outbid');
    if (f === 'winning') return card.classList.contains('card-winning');
    if (f === 'outbid')  return card.classList.contains('card-outbid');
    return true;
  }}

  document.querySelectorAll('.filter-btn[data-filter]').forEach(btn => {{
    btn.addEventListener('click', function() {{
      document.querySelectorAll('.filter-btn[data-filter]').forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      applyFilters();
    }});
  }});

  applyDismissed();
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML written to {output_path}")


# ══════════════════════════════════════════════════════════════
# ── RUN ───────────────────────────────────────────────────────

run_time = datetime.now()

hj_cutoff = (datetime.now(timezone.utc) + timedelta(hours=HJ_CLOSE_WITHIN_HOURS)) if HJ_CLOSE_WITHIN_HOURS else None
hb_cutoff = (datetime.now(timezone.utc) + timedelta(hours=HB_CLOSE_WITHIN_HOURS)) if HB_CLOSE_WITHIN_HOURS else None
ej_cutoff = (datetime.now(timezone.utc) + timedelta(hours=EJ_CLOSE_WITHIN_HOURS)) if EJ_CLOSE_WITHIN_HOURS else None

print("\nFetching HiBid account data...")
hibid_watchlist_ids, hibid_bid_status = fetch_hibid_account_lots()

# ── Tab 1: HiBid Jewelry
hj_cfg = {
    "include_cats":        HJ_INCLUDE_CATS,
    "exclude_cats":        HJ_EXCLUDE_CATS,
    "exclude_cat_strings": HJ_EXCLUDE_CAT_STRINGS,
    "exclude_auctioneers": HJ_EXCLUDE_AUCTIONEERS,
    "exclude_words":       [],
    "max_high_bid":        HJ_MAX_HIGH_BID,
    "max_min_bid":         HJ_MAX_MIN_BID,
    "shipping_offered":    HJ_SHIPPING_OFFERED,
    "min_pictures":        HJ_MIN_PICTURES,
    "max_pages":           HJ_MAX_PAGES,
    "use_jewelry_filters": True,
}
print(f"\nHiBid Jewelry fetching...")
all_hj = []
for cat_id in HJ_CATEGORY_IDS:
    print(f"  category {cat_id}...")
    all_hj.extend(fetch_hibid_lots(cat_id, hj_cfg, cutoff_dt=hj_cutoff,
                                   watchlist_ids=hibid_watchlist_ids, bid_status=hibid_bid_status))
hibid_jewelry = dedup_lots(all_hj)
hibid_jewelry.sort(key=lambda x: x["closes"] or "")

# ── Tab 2: HiBid Brands
hb_cfg = {
    "include_cats":        HB_INCLUDE_CATS,
    "exclude_cats":        HB_EXCLUDE_CATS,
    "exclude_cat_strings": HB_EXCLUDE_CAT_STRINGS,
    "exclude_auctioneers": HB_EXCLUDE_AUCTIONEERS,
    "exclude_words":       HB_EXCLUDE_WORDS,
    "max_high_bid":        HB_MAX_HIGH_BID,
    "max_min_bid":         HB_MAX_MIN_BID,
    "shipping_offered":    HB_SHIPPING_OFFERED,
    "min_pictures":        0,
    "max_pages":           HB_MAX_PAGES,
    "use_jewelry_filters": False,
}
print(f"\nHiBid Brands fetching...")
all_hb = []
for term in HB_SEARCH_TERMS:
    print(f"  {term}...")
    for cat_id in (HB_CATEGORY_IDS or [None]):
        all_hb.extend(fetch_hibid_lots(cat_id, hb_cfg, search_override=term, cutoff_dt=hb_cutoff,
                                       watchlist_ids=hibid_watchlist_ids, bid_status=hibid_bid_status))
hibid_brands = dedup_lots(all_hb)
hibid_brands.sort(key=lambda x: x["closes"] or "")

# ── EBTH followed items
print(f"\nFetching EBTH followed items...")
ebth_followed = fetch_ebth_followed_ids()

# ── Tab 3: EBTH (all categories merged)
ej_cfg = {
    "exclude_words":       EJ_EXCLUDE_WORDS,
    "max_high_bid":        EJ_MAX_HIGH_BID,
    "max_min_bid":         EJ_MAX_MIN_BID,
    "shipping_only":       EJ_SHIPPING_ONLY,
    "max_pages":           EJ_MAX_PAGES,
    "use_jewelry_filters": False,
}
print(f"\nEBTH fetching...")
all_ej = []
for path_slug in (EJ_PATH_SLUGS or [None]):
    print(f"  {path_slug}...")
    all_ej.extend(fetch_ebth_lots(path_slug, ej_cfg, cutoff_dt=ej_cutoff))
for lot in all_ej:
    lot["followed_status"] = ebth_followed.get(str(lot["id"]))
ebth_lots = dedup_lots(all_ej)
ebth_lots.sort(key=lambda x: x["closes"] or "")

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "hibid_results.html")

generate_html(hibid_jewelry, hibid_brands, ebth_lots, output_path, run_time)

success = webbrowser.open(f"file://{output_path}")
print("Browser open() returned:", success)
print("File exists:", os.path.exists(output_path))

webbrowser.open(output_path)