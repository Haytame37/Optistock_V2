"use client"

import type React from "react"
import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuth } from "@/providers/auth-provider"
import { toast } from "sonner"
import { Eye, EyeOff, Lock, CheckCircle2, AlertCircle, ArrowLeft } from "lucide-react"

export default function SignupPage() {
  const [form, setForm] = useState({ 
    role: "researcher", 
    first_name: "", 
    last_name: "", 
    email: "", 
    password: "",
    confirm_password: "" 
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const { signup } = useAuth()
  const router = useRouter()

  const getPasswordStrength = (pwd: string) => {
    let score = 0
    if (pwd.length >= 8) score++
    if (/[A-Z]/.test(pwd)) score++
    if (/[0-9]/.test(pwd)) score++
    if (/[^A-Za-z0-9]/.test(pwd)) score++
    return score
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.first_name || !form.last_name || !form.email || !form.password) {
      toast.error("Veuillez remplir tous les champs")
      return
    }
    if (form.password !== form.confirm_password) {
      toast.error("Les mots de passe ne correspondent pas")
      return
    }
    if (getPasswordStrength(form.password) < 2) {
      toast.error("Le mot de passe est trop faible")
      return
    }

    setLoading(true)
    try {
      const { confirm_password, ...signupData } = form
      await signup(signupData as any)
      toast.success("Compte créé avec succès")
      router.push("/login")
    } catch (err: any) {
      toast.error(err.response?.data?.detail || "Erreur lors de l'inscription")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 via-white to-slate-50 dark:from-slate-950 dark:via-slate-900 px-4 py-12">
      <Link 
        href="/" 
        className="absolute top-8 left-8 flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-primary transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Retour à l'accueil
      </Link>

      <Card className="w-full max-w-md shadow-xl border-none bg-card/80 backdrop-blur-sm">
        <CardHeader className="text-center">
          <Link href="/" className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold hover:scale-105 transition-transform shadow-lg shadow-primary/20">
            OS
          </Link>
          <CardTitle className="text-2xl font-bold">Créer un compte</CardTitle>
          <CardDescription>Rejoignez la plateforme OptiStock</CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Vous êtes un...</label>
              <Select value={form.role} onValueChange={(v) => setForm({ ...form, role: v })}>
                <SelectTrigger className="rounded-xl"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="researcher">Chercheur d'entrepôt</SelectItem>
                  <SelectItem value="owner">Propriétaire d'entrepôt</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Prénom</label>
                <Input className="rounded-xl" placeholder="Jean" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Nom</label>
                <Input className="rounded-xl" placeholder="Dupont" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Email professionnel</label>
              <Input className="rounded-xl" type="email" placeholder="jean@entreprise.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            </div>
            
            <div className="space-y-2">
              <label className="text-sm font-medium">Mot de passe</label>
              <div className="relative">
                <Input
                  className="rounded-xl pr-10"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              
              {/* Indicateur de force */}
              {form.password && (
                <div className="mt-2 space-y-1">
                  <div className="flex gap-1">
                    {[1, 2, 3, 4].map((level) => (
                      <div
                        key={level}
                        className={`h-1.5 flex-1 rounded-full transition-colors ${
                          level <= getPasswordStrength(form.password)
                            ? getPasswordStrength(form.password) <= 1 ? "bg-red-500" :
                              getPasswordStrength(form.password) <= 2 ? "bg-yellow-500" :
                              getPasswordStrength(form.password) <= 3 ? "bg-blue-500" : "bg-green-500"
                            : "bg-muted"
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                    {getPasswordStrength(form.password) <= 1 && <><AlertCircle className="h-3 w-3" /> Trop faible</>}
                    {getPasswordStrength(form.password) === 2 && "Moyen"}
                    {getPasswordStrength(form.password) === 3 && "Fort"}
                    {getPasswordStrength(form.password) === 4 && <><CheckCircle2 className="h-3 w-3 text-green-500" /> Très sécurisé</>}
                  </p>
                </div>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Confirmer le mot de passe</label>
              <Input
                className="rounded-xl"
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={form.confirm_password}
                onChange={(e) => setForm({ ...form, confirm_password: e.target.value })}
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full rounded-xl py-6 font-bold shadow-lg shadow-primary/20" disabled={loading}>
              {loading ? "Création en cours..." : "Créer mon compte"}
            </Button>
            <p className="text-sm text-muted-foreground text-center">
              Déjà un compte ?{" "}
              <Link href="/login" className="text-primary font-semibold hover:underline">Se connecter</Link>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}
