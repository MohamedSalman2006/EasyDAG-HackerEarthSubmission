from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
import secrets
from core.models import User, Conversation
from eth_account.messages import encode_defunct
from eth_account import Account
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from django.db.models import Sum
from .permissions import AllowGuestOrAuthenticated
from .models import Post, Vote
from .serializers import PostSerializer
from .agent_service import run_protocol_agent, run_simple_chat, run_simple_chat_stateless, run_protocol_agent_stateless
import json

from django.http import HttpResponse, Http404

def login_page(request):
    return render(request, "index.html")

def home(request):
    return render(request, "home.html")

def contract_page(request):
    return render(request, "contract.html")

def community_page(request):
    return render(request, "community.html")

def market_page(request):
    return render(request, "market.html")

@api_view(['GET'])
@permission_classes([AllowAny])
def get_login_nonce(request):
    nonce = secrets.token_hex(32)
    request.session['login_nonce'] = nonce
    return Response({'nonce': nonce})

@api_view(['POST'])
@permission_classes([AllowAny])
def wallet_login(request):
    try:
        data = json.loads(request.body)
        wallet_address = data['wallet_address']
        signature=data['signature']
        message=data['message']

        print("Login attempt")
        print("Wallet Address:", wallet_address)
        print("Message:", message)
        print("Signature:", signature)

        nonce = request.session.get('login_nonce')

        if not nonce:
            return Response({"error": "Nonce not found in session. Please request a new one."}, status=400)


        if message != nonce:
            print("Message mismatch")
            return Response({"error": "Invalid nonce signed"}, status=400)

        encoded_message = encode_defunct(hexstr="0x" + message)
        recovered_address = Account.recover_message(encoded_message, signature=signature)

        print("Recovered address:", recovered_address)
        print("Wallet address:", wallet_address)

        if recovered_address.lower() != wallet_address.lower():
            return Response({"error": "Signature mismatch"}, status=401)
        
        request.session.pop('login_nonce', None)
        
        user, _ = User.objects.get_or_create(wallet_address=wallet_address)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'wallet_address': user.wallet_address
        })

    except Exception as e:
        return Response({"error": str(e)}, status=400)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({"message": "Token valid"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def secure_home(request):
    return render(request, "home.html")

@api_view(['POST'])
@permission_classes([AllowGuestOrAuthenticated])
def smart_contract_api(request):
    try:
        data = json.loads(request.body)
        prompt = data.get("prompt")
        mode = data.get("mode", "conversational")

        if not prompt:
            return JsonResponse({"error": "Prompt missing!"}, status=400)

        result = None
        if request.user.is_authenticated:
            if mode == 'protocol_builder':
                result = run_protocol_agent(user=request.user, new_prompt=prompt)
            else:
                result = run_simple_chat(user=request.user, new_prompt=prompt)
        else:
            history = data.get("history", [])
            if mode == 'protocol_builder':
                result = run_protocol_agent_stateless(prompt, history)
            else: 
                result = run_simple_chat_stateless(prompt, history)

      
        if not result or result.get('error'):
            return JsonResponse({"error": result.get('error', 'An unknown error occurred.')}, status=400)

        if 'protocol_params' in result:
            protocol_params = result.get('protocol_params', {})
            protocol_type = protocol_params.get('protocol_type', 'Custom')
            response_data = {
                "protocol": {
                    "name": f"{protocol_type.capitalize()} Protocol",
                    "explanation": result.get('explanation', ''),
                    "contracts": [{
                        "name": f"{protocol_type.capitalize()}.sol",
                        "code": result.get('modified_code', '# No code was generated.')
                    }]
                }
            }
        else: 
            response_data = {"response": result.get("response")}
        
        return JsonResponse(response_data, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def new_conversation(request):
    """
    Deletes the current conversation history for the authenticated user.
    """
    user = request.user
    conversation, _ = Conversation.objects.get_or_create(user=user)
    conversation.messages.all().delete()
    return Response({"status": "success", "message": "Conversation history cleared."}, status=200)

class PostListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.annotate(score=Sum('votes__vote_type')).order_by('-score')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostVoteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        vote_type = request.data.get('vote_type')
        if vote_type not in [1, -1]:
            return Response({"error": "Invalid vote type."}, status=status.HTTP_400_BAD_REQUEST)

        post = Post.objects.get(pk=pk)
        Vote.objects.update_or_create(
            user=request.user, post=post,
            defaults={'vote_type': vote_type}
        )
        return Response(status=status.HTTP_200_OK)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def get_contract_template(request, contract_name):
    """
    Securely serves a specified smart contract template from the filesystem.
    """
    valid_contracts = ['Staking', 'Token', 'Vesting']

    formatted_name = contract_name.capitalize()

    if formatted_name not in valid_contracts:
        raise Http404("Contract template not found.")
    
    template_path = settings.BASE_DIR/'protocol_template'/f'{formatted_name}.sol'

    if template_path.is_file():
        content = template_path.read_text()
        return HttpResponse(content, content_type='text/plain')
    else:
        raise Http404("Contract template file does not exist")