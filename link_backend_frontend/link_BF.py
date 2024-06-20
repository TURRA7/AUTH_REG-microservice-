from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi_cache.decorator import cache
from fastapi.templating import Jinja2Templates


# Указываем папку для чтения html шаблонов
templates = Jinja2Templates(directory="templates")


class TemplateHandler:
    """Класс рендеринга html шаблонов."""

    def __init__(self, router: APIRouter, route: str, template_path: str):
        """Инициализация необходимых параметров."""
        self.router = router
        self.route = route
        self.template_path = template_path
        self.router.add_api_route(self.route, self.handler_request,
                                  methods=["GET"], response_class=HTMLResponse)

    @cache(expire=60)
    async def get_rendered_template(self, template_name: str,
                                    context: dict) -> str:
        """Метод рендерит html шаблон в строку и кэширует его."""
        template = templates.get_template(template_name)
        return template.render(context)

    async def handler_request(self, request: Request) -> HTMLResponse:
        """Метод возвращает отрендеренный шаблон"""
        context = {"request": request}
        html_content = await self.get_rendered_template(
            self.template_path, context)
        return HTMLResponse(content=html_content)
