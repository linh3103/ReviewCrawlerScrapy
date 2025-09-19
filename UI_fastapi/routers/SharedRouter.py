from fastapi import APIRouter, HTTPException

router = APIRouter (
    prefix="/api/shared",
    tags=['Shared']
)

NAVER_BRANDS_DATA = {
    "바자르": "https://brand.naver.com/bazaar/products/",
    "라뽐므": "https://brand.naver.com/lapomme/products/",
    "쁘리엘르": "https://brand.naver.com/prielle/products/",
    "마틸라": "https://brand.naver.com/maatila/products/",
    "그래이불": "https://brand.naver.com/yesbedding/products/",
    "믹스앤매치": "https://brand.naver.com/mixandmatch/products/",
    "누비지오": "https://brand.naver.com/nubizio/products/",
    "데코뷰": "https://brand.naver.com/decoview/products/",
    "깃든": "https://brand.naver.com/gitden/products/",
    "스타일링홈": "https://brand.naver.com/styhome/products/",
    "아망떼": "https://brand.naver.com/amante/products/",
    "호무로": "https://brand.naver.com/homuro/products/",
    "헬로우슬립": "https://brand.naver.com/hellosleep/products/",
    "오넬로이": "https://smartstore.naver.com/oneloi/products/",
    "플로라": "https://brand.naver.com/flora/products/",
    "르올": "https://smartstore.naver.com/mewansungmall/products/",
    "에이트룸": "https://brand.naver.com/8room/products/",
    "베이직톤": "https://brand.naver.com/basictone/products/",
    "아토앤알로": "https://brand.naver.com/beddingnara/products/",
    "바숨": "https://brand.naver.com/busum/products/",
    "올리비아데코": "https://brand.naver.com/oliviadeco/products/",
    "코지네스트": "https://brand.naver.com/cozynest/products/",
    "메종오트몬드": "https://smartstore.naver.com/hautemonde/products/",
    "바운티풀": "https://brand.naver.com/bountiful/products/",
    "도아드림": "https://brand.naver.com/doadream_goose/products/",
    "CROWN GOOSE": "https://brand.naver.com/crowngoose/products/"
}

@router.get("/naver_brands")
def get_naver_brands():
    try:
        return {
            'status': 'success',
            'naver_brands': NAVER_BRANDS_DATA
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
        