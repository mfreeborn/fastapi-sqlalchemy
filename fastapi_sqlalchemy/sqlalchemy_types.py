from sqlalchemy import BigInteger, TypeDecorator


class BigIntegerType(TypeDecorator):
    impl = BigInteger
