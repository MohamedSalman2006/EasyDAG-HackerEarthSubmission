from django.urls import path
from .views import login_page, wallet_login, get_login_nonce, home, contract_page, market_page, community_page, smart_contract_api, new_conversation, get_contract_template
from .views import PostListCreateAPIView, PostVoteAPIView

urlpatterns = [
    path('', login_page),  
    path('login/', login_page, name='login-page'),
    path('api/login/', wallet_login, name='wallet-login'),
    path('api/get-nonce/', get_login_nonce, name='get-nonce'),
    path('home/', home, name='home'),
    path('contract/', contract_page, name='contract-page'),
    path('api/get-template/<str:contract_name>/', get_contract_template, name='get-contact-template'),
    path('market/', market_page, name='market-page'),
    path("api/generate-contract/", smart_contract_api, name="generate-contract"),
    path("api/build-protocol/", smart_contract_api, name="build-protocol"),
    path('community/', community_page, name='community-page'),
    path("api/new-conversation/", new_conversation, name="new-conversation"),
    path('api/posts/', PostListCreateAPIView.as_view(), name='post-list-create'),
    path('api/posts/<int:pk>/vote/', PostVoteAPIView.as_view(), name='post-vote'),
]
