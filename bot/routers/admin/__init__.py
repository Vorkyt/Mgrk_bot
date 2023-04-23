from ...filters.admin import AdminFilter
from ...utils.router import Router
from .. import root_handlers_router

router = Router()
router.bind_filter(AdminFilter())
root_handlers_router.include_router(router)
