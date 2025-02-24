from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Identity
from sqlalchemy.orm import relationship
from database import Base

class Brand(Base):
    """
    브랜드 테이블:
    - 브랜드사의 기본 정보
        - 화장품 컨셉....이런 것도 다 받아야 할 것 같은데 더 고민 필요
    - 브랜드사 프로젝트 정보 -> 추후 분리 필요함 꼭!
    """
    __tablename__ = "brands"
    
    id = Column(Integer, Identity(start=1, increment=1) ,primary_key=True)
    # 브랜드 코드 : 링크 생성
    # code = Column(String, nullable=False, unique=True)
    brand_name = Column(String, index=True, nullable=False, comment="브랜드명: 로그인화면에서 브랜드별 구분할 때 사용")
    capital = Column(Integer, nullable=True, comment="회사 자본금")
    min_price = Column(Integer, nullable=False, comment="최소 단가")
    max_price = Column(Integer, nullable=False, comment="최대 단가")
    price = Column(Integer, nullable=False, comment="목표 단가: 단가 같은 경우엔 사용자가 범위로 지정하게 할 지도 고민중")
    moq = Column(Integer, nullable=False, comment="최소 주문 수량")
    planned_launch = Column(String, nullable=True, comment="납품 기한")

    # ================ 여기서부터 프로젝트로 따로 분리마려움 ============
    
    represetative_info = Column(String, nullable=True, comment="대표자 정보: 이름..?(x)/ 경력 / 학력.. 일단 이정도")
    history = Column(String, nullable=True, comment="회사 연혁: milestone!")
    performance = Column(String, nullable=True, comment="회사 성과: 솔직히 연혁이랑 어떤 차이인지 잘 모르겠다./ 업적과 성과의 차인가")
    marketing_plan = Column(String, nullable=True, comment="앞으로의 마케팅 계획 : 어떻게 마케팅할 지 / 인플루언서 / 마케팅 채널")
    business_plan = Column(String, nullable=True, comment="앞으로의 사업 계획: 제품 개발 / 시장 진출.. 등등")

    # =============== 이 부분은 왜 있는지 솔직히 잘 모르겠음 =================
    created_at = Column(DateTime, default=func.now())