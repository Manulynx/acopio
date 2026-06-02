from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import CustomUser, Perfil


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )
    
    cedula = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000000000',
            'pattern': r'\d{11}',
            'title': 'Debe contener exactamente 11 dígitos'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+53 5XXXXXXX'
        })
    )
    
    cargo = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cargo en la empresa'
        })
    )
    
    departamento = forms.ChoiceField(
        choices=[('', '-- Seleccionar --')] + CustomUser._meta.get_field('departamento').choices,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    fecha_ingreso = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'cedula', 'telefono', 'cargo', 'departamento', 
            'fecha_ingreso', 'password1', 'password2'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar widgets de campos heredados
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
        
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })

    def clean_cedula(self):
        """Validar formato de cédula"""
        cedula = self.cleaned_data.get('cedula') or None
        if not cedula:
            return None

        if len(cedula) != 11:
            raise ValidationError("La cédula debe tener exactamente 11 dígitos")
        if not cedula.isdigit():
            raise ValidationError("La cédula debe contener solo números")
        if CustomUser.objects.filter(cedula=cedula).exists():
            raise ValidationError("Ya existe un usuario con esta cédula")

        return cedula

    def clean_email(self):
        """Validar que el email no exista"""
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email")
        return email

    def save(self, commit=True):
        """Guardar usuario con campos adicionales"""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.cedula = self.cleaned_data.get('cedula') or None
        user.telefono = self.cleaned_data.get('telefono')
        user.cargo = self.cleaned_data.get('cargo')
        user.departamento = self.cleaned_data.get('departamento')
        user.fecha_ingreso = self.cleaned_data.get('fecha_ingreso')
        
        if commit:
            user.save()
            # Crear perfil automáticamente
            Perfil.objects.get_or_create(usuario=user)
            
        return user


class CustomUserChangeForm(UserChangeForm):
    """Formulario personalizado para editar usuarios"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    cedula = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': r'\d{11}'
        })
    )
    
    telefono = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    direccion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    
    cargo = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    departamento = forms.ChoiceField(
        choices=[('', '-- Seleccionar --')] + CustomUser._meta.get_field('departamento').choices,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    fecha_ingreso = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    salario = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01'
        })
    )
    
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    # Campos opcionales de cambio de contraseña
    password1 = forms.CharField(
        label="Nueva contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Dejar vacío para no cambiar'
        })
    )
    
    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'cedula', 'telefono', 'direccion', 'cargo', 
            'departamento', 'fecha_ingreso', 'salario',
            'avatar', 'is_active', 'is_staff'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Remover el campo password que viene por defecto
        if 'password' in self.fields:
            del self.fields['password']
        
        # Personalizar widgets
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        
        # Configurar campos de permisos solo para staff/superuser
        self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['is_staff'].widget.attrs.update({'class': 'form-check-input'})

    def clean_cedula(self):
        """Validar cédula sin conflictos"""
        cedula = self.cleaned_data.get('cedula') or None
        if not cedula:
            return None

        if len(cedula) != 11 or not cedula.isdigit():
            raise ValidationError("La cédula debe tener exactamente 11 dígitos")

        # Verificar duplicados excluyendo el usuario actual
        existing_user = CustomUser.objects.filter(cedula=cedula).exclude(pk=self.instance.pk)
        if existing_user.exists():
            raise ValidationError("Ya existe un usuario con esta cédula")

        return cedula

    def clean_email(self):
        """Validar email sin conflictos"""
        email = self.cleaned_data.get('email')
        if email:
            existing_user = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
            if existing_user.exists():
                raise ValidationError("Ya existe un usuario con este email")
        
        return email

    def clean(self):
        """Validar contraseñas si se proporcionan"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                raise ValidationError("Las contraseñas no coinciden")
            
            if len(password1) < 8:
                raise ValidationError("La contraseña debe tener al menos 8 caracteres")

        return cleaned_data

    def save(self, commit=True):
        """Guardar usuario con cambios de contraseña si aplica"""
        user = super().save(commit=False)
        
        # Cambiar contraseña si se proporcionó una nueva
        password1 = self.cleaned_data.get('password1')
        if password1:
            user.set_password(password1)
        
        # Normalizar cédula vacía a None antes de guardar
        user.cedula = self.cleaned_data.get('cedula') or None

        if commit:
            user.save()
            # Asegurar que existe perfil
            Perfil.objects.get_or_create(usuario=user)
        
        return user


class LoginForm(forms.Form):
    """Formulario personalizado de login"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario',
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            # Verificar si el usuario existe
            try:
                user = CustomUser.objects.get(username=username)
                
                # Verificar si está bloqueado
                if user.esta_bloqueado:
                    raise ValidationError(
                        f"Usuario bloqueado hasta {user.bloqueado_hasta.strftime('%d/%m/%Y %H:%M')}"
                    )
                
                # Intentar autenticar
                self.user_cache = authenticate(
                    self.request, 
                    username=username, 
                    password=password
                )
                
                if self.user_cache is None:
                    # Incrementar intentos fallidos
                    user.incrementar_intentos_fallidos()
                    raise ValidationError("Nombre de usuario o contraseña incorrectos")
                else:
                    # Reset intentos fallidos en login exitoso
                    user.resetear_intentos_fallidos()
                    
            except CustomUser.DoesNotExist:
                raise ValidationError("Nombre de usuario o contraseña incorrectos")

        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class PerfilForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    
    class Meta:
        model = Perfil
        fields = (
            'biografia', 'especialidades', 'certificaciones',
            'linkedin', 'twitter',
            'mostrar_email_publico', 'mostrar_telefono_publico', 
            'perfil_publico'
        )
        widgets = {
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos sobre ti...'
            }),
            'especialidades': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Especialidad 1, Especialidad 2, ...'
            }),
            'certificaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Lista tus certificaciones...'
            }),
            'linkedin': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://linkedin.com/in/tu-perfil'
            }),
            'twitter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@tu_usuario'
            }),
            'mostrar_email_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_telefono_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'perfil_publico': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar contraseña"""
    
    password_actual = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual'
        })
    )
    
    password_nueva = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
    )
    
    password_confirmacion = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_password_actual(self):
        """Verificar contraseña actual"""
        password_actual = self.cleaned_data.get('password_actual')
        if not self.user.check_password(password_actual):
            raise ValidationError("La contraseña actual es incorrecta")
        return password_actual

    def clean(self):
        """Validar que las nuevas contraseñas coincidan"""
        cleaned_data = super().clean()
        password_nueva = cleaned_data.get('password_nueva')
        password_confirmacion = cleaned_data.get('password_confirmacion')

        if password_nueva and password_confirmacion:
            if password_nueva != password_confirmacion:
                raise ValidationError("Las nuevas contraseñas no coinciden")
            
            if len(password_nueva) < 8:
                raise ValidationError("La nueva contraseña debe tener al menos 8 caracteres")

        return cleaned_data

    def save(self):
        """Guardar nueva contraseña"""
        password = self.cleaned_data['password_nueva']
        self.user.set_password(password)
        self.user.ultimo_cambio_password = timezone.now()
        self.user.requiere_cambio_password = False
        self.user.save()
        return self.user