from fastapi import Request

from ausikor_common.utility.constant.settings import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings