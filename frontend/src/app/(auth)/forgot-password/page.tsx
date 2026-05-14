"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "sonner"
import api from "@/services/api"
import { Eye, EyeOff, Mail, Lock, CheckCircle2, ArrowLeft } from "lucide-react"

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<"email" | "otp" | "reset" | "success">("email")
  const [email, setEmail] = useState("")
  const [otp, setOtp] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  const handleSendOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return toast.error("Veuillez entrer votre email")
    setLoading(true)
    try {
      await api.post("/auth/forgot-password", { email })
      toast.success("Code envoyé ! Vérifiez votre boîte mail.")
      setStep("otp")
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Erreur lors de l'envoi du code")
    } finally {
      setLoading(false)
    }
  }

  const handleVerifyOTP = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!otp) return toast.error("Veuillez entrer le code")
    setLoading(true)
    try {
      await api.post("/auth/verify-otp", { email, otp_code: otp })
      setStep("reset")
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Code invalide ou expiré")
    } finally {
      setLoading(false)
    }
  }

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (newPassword !== confirmPassword) return toast.error("Les mots de passe ne correspondent pas")
    if (newPassword.length < 8) return toast.error("Le mot de passe doit faire au moins 8 caractères")
    setLoading(true)
    try {
      await api.post("/auth/reset-password", { email, otp_code: otp, new_password: newPassword })
      setStep("success")
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Erreur lors de la réinitialisation")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 px-4">
      <Card className="w-full max-w-md shadow-xl border-none bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold text-xl shadow-lg shadow-primary/20">
            {step === "success" ? <CheckCircle2 className="h-6 w-6" /> : "OS"}
          </div>
          <CardTitle className="text-2xl font-bold">
            {step === "email" && "Mot de passe oublié"}
            {step === "otp" && "Vérification"}
            {step === "reset" && "Nouveau mot de passe"}
            {step === "success" && "Succès !"}
          </CardTitle>
          <CardDescription>
            {step === "email" && "Récupérez l'accès à votre compte OptiStock"}
            {step === "otp" && `Entrez le code envoyé à ${email}`}
            {step === "reset" && "Choisissez un mot de passe robuste"}
            {step === "success" && "Votre mot de passe a été mis à jour"}
          </CardDescription>
        </CardHeader>

        <CardContent>
          {step === "email" && (
            <form onSubmit={handleSendOTP} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Email professionnel</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type="email"
                    placeholder="nom@entreprise.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Envoi..." : "Envoyer le code OTP"}
              </Button>
            </form>
          )}

          {step === "otp" && (
            <form onSubmit={handleVerifyOTP} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-center block">Code de vérification (6 chiffres)</label>
                <Input
                  type="text"
                  placeholder="000000"
                  maxLength={6}
                  value={otp}
                  onChange={(e) => setOtp(e.target.value)}
                  className="text-center text-2xl tracking-[0.5em] font-mono py-6"
                  required
                />
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Vérification..." : "Vérifier le code"}
              </Button>
              <Button variant="ghost" className="w-full text-xs" onClick={() => setStep("email")}>
                Réessayer avec un autre email
              </Button>
            </form>
          )}

          {step === "reset" && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Nouveau mot de passe</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-3 text-muted-foreground hover:text-foreground"
                  >
                    {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Confirmer le mot de passe</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>
              <Button type="submit" className="w-full" disabled={loading}>
                {loading ? "Mise à jour..." : "Réinitialiser le mot de passe"}
              </Button>
            </form>
          )}

          {step === "success" && (
            <div className="text-center py-4">
              <p className="text-muted-foreground mb-6">Vous pouvez maintenant vous connecter avec vos nouveaux identifiants.</p>
              <Button className="w-full" onClick={() => router.push("/login")}>
                Aller à la connexion
              </Button>
            </div>
          )}
        </CardContent>

        {step !== "success" && (
          <CardFooter>
            <Link href="/login" className="text-sm text-muted-foreground hover:text-primary flex items-center gap-2 mx-auto transition-colors">
              <ArrowLeft className="h-4 w-4" /> Retour à la connexion
            </Link>
          </CardFooter>
        )}
      </Card>
    </div>
  )
}
