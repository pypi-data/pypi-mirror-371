from fourlabs_auth.models import UserToken, TokenUsageLog
from django.utils import timezone


class TokenManagerService:
    @staticmethod
    def _check_and_reset(user_token: UserToken):
        today = timezone.now().date()
        if user_token.last_reset < today:
            user_token.tokens_restantes = user_token.total_tokens_diarios
            user_token.last_reset = today
            user_token.save()
            # registra o reset
            TokenUsageLog.objects.create(
                user=user_token.user,
                action="RESET",
                quantidade=user_token.total_tokens_diarios,
                tokens_restantes=user_token.tokens_restantes
            )

    @staticmethod
    def spend_tokens(user, quantidade: int) -> bool:
        user_token, _ = UserToken.objects.get_or_create(user=user)
        TokenManagerService._check_and_reset(user_token)

        if user_token.tokens_restantes >= quantidade:
            user_token.tokens_restantes -= quantidade
            user_token.save()
            # registra o gasto
            TokenUsageLog.objects.create(
                user=user,
                action="SPEND",
                quantidade=-quantidade,
                tokens_restantes=user_token.tokens_restantes
            )
            return True
        return False

    @staticmethod
    def add_tokens(user, quantidade: int):
        user_token, _ = UserToken.objects.get_or_create(user=user)
        TokenManagerService._check_and_reset(user_token)

        user_token.tokens_restantes += quantidade
        if user_token.tokens_restantes > user_token.total_tokens_diarios:
            user_token.tokens_restantes = user_token.total_tokens_diarios
        user_token.save()

        # registra o acréscimo
        TokenUsageLog.objects.create(
            user=user,
            action="ADD",
            quantidade=quantidade,
            tokens_restantes=user_token.tokens_restantes
        )

    @staticmethod
    def reset_tokens(user):
        user_token, _ = UserToken.objects.get_or_create(user=user)
        user_token.tokens_restantes = user_token.total_tokens_diarios
        user_token.last_reset = timezone.now().date()
        user_token.save()

        # registra o reset manual
        TokenUsageLog.objects.create(
            user=user,
            action="RESET",
            quantidade=user_token.total_tokens_diarios,
            tokens_restantes=user_token.tokens_restantes
        )

    @staticmethod
    def get_tokens_remaining(user) -> int:
        user_token, _ = UserToken.objects.get_or_create(user=user)
        TokenManagerService._check_and_reset(user_token)
        return user_token.tokens_restantes
