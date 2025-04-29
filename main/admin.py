from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404

from .models import Product, Category, Brand, Feedback
from django.utils.html import format_html  # для вставки HTML в админку
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.urls import path  # Добавьте этот импорт
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.admin import AdminSite
from .models import Feedback
from django.template.response import TemplateResponse
from django.contrib import admin, messages

# Убираем модели пользователей и групп
admin.site.unregister(User)
admin.site.unregister(Group)

# Убираем действия для всех моделей
class NoActionsAdmin(admin.ModelAdmin):
    actions = None

# Применяем этот класс ко всем моделям
admin.site.site_header = "Моя админка"  # Заголовок на странице админки
admin.site.site_title = "Админ панель"

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image_preview', 'category_name', 'brand_name')
    list_filter = ('category', 'brand')
    search_fields = ('name', 'category__name', 'brand__name')
    actions = None  # Отключаем все действия, включая "Выполнить"

    # Отображение миниатюрной картинки
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Миниатюра'

    # Отображение названия категории
    def category_name(self, obj):
        return obj.category.name if obj.category else 'Не указана'
    category_name.short_description = 'Категория'

    # Отображение названия бренда
    def brand_name(self, obj):
        return obj.brand.name if obj.brand else 'Не указан'
    brand_name.short_description = 'Бренд'


# Кастомный виджет для отображения сообщения от клиентов
class CustomAdminSite(AdminSite):
    site_header = "Администрирование сайта"

    def get_app_list(self, request):
        # Получаем стандартный список приложений
        app_list = super().get_app_list(request)

        # Удаляем модель Feedback из списка
        for app in app_list:
            app['models'] = [model for model in app['models'] if model['object_name'] != 'Feedback']
        return app_list

    def index(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}

        # Важное добавление
        app_list = self.get_app_list(request)
        extra_context['app_list'] = app_list

        extra_context['custom_content'] = 'admin/custom_block.html'
        extra_context['feedback_count'] = Feedback.objects.filter(is_read=False).count()

        return TemplateResponse(request, 'admin/custom_index.html', extra_context)


    def get_admin_panel(self, request):
        feedback_count = Feedback.objects.filter(is_read=False).count()
        # Создаем кастомную панель с красным кружком и количеством непрочитанных сообщений
        return format_html(
            f'<div class="custom-admin-panel">'
            f'<a href="{reverse("admin:view_feedbacks")}" class="text-decoration-none">'
            f'<span class="badge badge-danger">{feedback_count}</span> '
            f'Сообщения от клиентов'
            f'</a></div>'
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('feedback/<int:pk>/mark_read/', self.admin_view(self.mark_feedback_as_read), name='mark_feedback_as_read'),
           # path('feedbacks/', self.admin_view(self.view_feedbacks), name='view_feedbacks'),
        ]
        return custom_urls + urls

    def mark_feedback_as_read(self, request, pk):
        feedback = get_object_or_404(Feedback, pk=pk)
        feedback.is_read = True
        feedback.save()
        messages.success(request, f"Сообщение от {feedback.name} отмечено как прочитанное.")
        return redirect("admin:main_feedback_changelist")

    def get_unread_feedback_count(self, request):
        from .models import Feedback
        count = Feedback.objects.filter(is_read=False).count()
        return JsonResponse({'unread_count': count})


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read', 'mark_as_read_link')
    list_filter = ('is_read',)
    actions = ['mark_as_read']

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.order_by('-created_at')

    def mark_as_read(self, request, queryset):
        updated_count = queryset.update(is_read=True)
        self.message_user(request, f'Отметить как прочитанные: {updated_count} сообщение(й)')
    mark_as_read.short_description = 'Отметить как прочитанные'

    def mark_as_read_link(self, obj):
        if not obj.is_read:
            url = reverse('admin:mark_feedback_as_read', args=[obj.pk])
            return format_html('<a class="button" href="{}">Отметить</a>', url)
        return "✓"
    mark_as_read_link.short_description = 'Прочитано'


# # Регистрируем кастомный виджет и модель в админке
admin_site = CustomAdminSite()

admin_site.register(Feedback, FeedbackAdmin)
# Регистрируем модель в админке
admin_site.register(Product, ProductAdmin)
admin_site.register(Category)
admin_site.register(Brand)
