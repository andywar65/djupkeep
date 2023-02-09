from django.urls import path
from django.utils.translation import gettext_lazy as _

from .views.activity_views import (
    ActivityCreateDismissView,
    ActivityCreateView,
    ActivityDetailView,
    ActivityUpdateView,
)
from .views.category_views import (
    CategoryCreateDismissView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryDetailActivityListView,
    CategoryDetailRefreshView,
    CategoryDetailRelatedView,
    CategoryDetailView,
    CategoryListView,
    CategoryListWrapperView,
    CategoryMoveDownView,
    CategoryMoveUpView,
    CategoryUpdateView,
    IntroTemplateView,
)
from .views.element_views import (
    ElementCreateLocatedView,
    ElementCreateView,
    ElementDeleteView,
    ElementDetailView,
    ElementListView,
    ElementUpdateView,
)
from .views.location_views import (
    LocationCreateView,
    LocationDeleteView,
    LocationDetailView,
    LocationListView,
    LocationUpdateView,
)

app_name = "djupkeep"
urlpatterns = [
    path(
        "",
        IntroTemplateView.as_view(),
        name="introduction",
    ),
    path(
        _("location/list/"),
        LocationListView.as_view(),
        name="location_list",
    ),
    path(
        _("location/add/"),
        LocationCreateView.as_view(),
        name="location_create",
    ),
    path(
        _("location/<pk>/"),
        LocationDetailView.as_view(),
        name="location_detail",
    ),
    path(
        _("location/<pk>/change/"),
        LocationUpdateView.as_view(),
        name="location_change",
    ),
    path(
        _("location/<pk>/delete/"),
        LocationDeleteView.as_view(),
        name="location_delete",
    ),
    path(
        _("location/<pk>/element/add/"),
        ElementCreateLocatedView.as_view(),
        name="element_create_located",
    ),
    path(
        _("category/list/"),
        CategoryListView.as_view(),
        name="category_list",
    ),
    path(
        "category/list/wrapper/",
        CategoryListWrapperView.as_view(),
        name="category_list_wrapper",
    ),
    path(
        "category/add/",
        CategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "category/add/dismiss/",
        CategoryCreateDismissView.as_view(),
        name="category_create_dismiss",
    ),
    path(
        "category/<pk>/",
        CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "category/<pk>/refresh/",
        CategoryDetailRefreshView.as_view(),
        name="category_detail_refresh",
    ),
    path(
        _("category/<pk>/related/"),
        CategoryDetailRelatedView.as_view(),
        name="category_detail_related",
    ),
    path(
        "category/<pk>/activity/list/",
        CategoryDetailActivityListView.as_view(),
        name="activity_list",
    ),
    path(
        "category/<pk>/change/",
        CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path(
        "category/<pk>/move/down/",
        CategoryMoveDownView.as_view(),
        name="category_move_down",
    ),
    path(
        "category/<pk>/move/up/",
        CategoryMoveUpView.as_view(),
        name="category_move_up",
    ),
    path(
        "category/<pk>/delete/",
        CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    path(
        _("element/list/"),
        ElementListView.as_view(),
        name="element_list",
    ),
    path(
        _("element/add/"),
        ElementCreateView.as_view(),
        name="element_create",
    ),
    path(
        _("element/<pk>/"),
        ElementDetailView.as_view(),
        name="element_detail",
    ),
    path(
        _("element/<pk>/change/"),
        ElementUpdateView.as_view(),
        name="element_update",
    ),
    path(
        _("element/<pk>/delete/"),
        ElementDeleteView.as_view(),
        name="element_delete",
    ),
    path(
        "category/<pk>/activity/add/",
        ActivityCreateView.as_view(),
        name="activity_create",
    ),
    path(
        "category/<pk>/activity/add/dismiss/",
        ActivityCreateDismissView.as_view(),
        name="activity_create_dismiss",
    ),
    path(
        "activity/<pk>/",
        ActivityDetailView.as_view(),
        name="activity_detail",
    ),
    path(
        "activity/<pk>/change/",
        ActivityUpdateView.as_view(),
        name="activity_update",
    ),
]
