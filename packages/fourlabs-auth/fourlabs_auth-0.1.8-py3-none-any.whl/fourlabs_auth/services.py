from fourlabs_auth.models import UserToken
from django.utils import timezone


class TokenManagerService:
    @staticmethod
    def _check_and_reset(user_token: UserToken):
        """Reseta tokens se já virou o dia."""
        today = timezone.now().date()
        if user_token.last_reset < today:
            user_token.tokens_restantes = user_token.total_tokens_diarios
            user_token.last_reset = today
            user_token.save()

    @staticmethod
    def spend_tokens(user, quantidade: int) -> bool:
        """Tenta gastar tokens de um usuário. Retorna True se conseguir, False se não houver tokens suficientes."""
        user_token, _ = UserToken.objects.get_or_create(user=user)
        TokenManagerService._check_and_reset(user_token)

        if user_token.tokens_restantes >= quantidade:
            user_token.tokens_restantes -= quantidade
            user_token.save()
            return True
        return False

    @staticmethod
    def add_tokens(user, quantidade: int):
        """Adiciona uma quantidade de tokens ao usuário (não reseta o limite diário)."""
        user_token, _ = UserToken.objects.get_or_create(user=user)
        TokenManagerService._check_and_reset(user_token)

        user_token.tokens_restantes += quantidade
        # Não pode passar do limite diário
        if user_token.tokens_restantes > user_token.total_tokens_diarios:
            user_token.tokens_restantes = user_token.total_tokens_diarios
        user_token.save()

    @staticmethod
    def reset_tokens(user):
        """Reseta manualmente os tokens do usuário para o total diário."""
        user_token, _ = UserToken.objects.get_or_create(user=user)
        user_token.tokens_restantes = user_token.total_tokens_diarios
        user_token.last_reset = timezone.now().date()
        user_token.save()

    @staticmethod
    def get_tokens_remaining(user) -> int:
        """Retorna quantos tokens o usuário ainda tem no dia."""
        user_token, _ = UserToken.objects.get_or_create(user=user)
        TokenManagerService._check_and_reset(user_token)
        return user_token.tokens_restantes
