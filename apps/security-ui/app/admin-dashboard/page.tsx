"use client"

import React, { useEffect, useState } from "react"
import { Users, CheckCircle, XCircle, Clock, Shield, Search, RefreshCcw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Input } from "@/components/ui/input"
import { getPendingVisitors, approveVisitor, declineVisitor, HttpError } from "@/lib/api"
import { useSession } from "@/hooks/use-session"
import AccessDenied from "@/components/access-denied"
import { toast } from "sonner"

export default function AdminDashboardPage() {
  const { loading: sessionLoading, authenticated, user } = useSession({ redirectToLogin: true })
  const [pendingVisitors, setPendingVisitors] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [actioningId, setActioningId] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState("")

  const fetchPending = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const res = await getPendingVisitors()
      setPendingVisitors(res.visitors || [])
    } catch (e) {
      setError(e instanceof HttpError ? e.message : "Failed to load pending visitors")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!sessionLoading && authenticated && user?.role === "admin") {
      fetchPending()
    }
  }, [authenticated, sessionLoading, user?.role])

  const handleApprove = async (visitorId: string) => {
    setActioningId(visitorId)
    try {
      await approveVisitor(visitorId)
      toast.success("Visitor approved successfully")
      setPendingVisitors((prev) => prev.filter((v) => {
        const id = v.visitorId || v.visitor_id || v.id
        return id !== visitorId
      }))
    } catch (e) {
      toast.error(e instanceof HttpError ? e.message : "Failed to approve visitor")
    } finally {
      setActioningId(null)
    }
  }

  const handleDecline = async (visitorId: string) => {
    const reason = window.prompt("Reason for declining:")
    if (reason === null) return

    setActioningId(visitorId)
    try {
      await declineVisitor(visitorId, reason || "No reason provided")
      toast.success("Visitor declined")
      setPendingVisitors((prev) => prev.filter((v) => {
        const id = v.visitorId || v.visitor_id || v.id
        return id !== visitorId
      }))
    } catch (e) {
      toast.error(e instanceof HttpError ? e.message : "Failed to decline visitor")
    } finally {
      setActioningId(null)
    }
  }

  if (!sessionLoading && authenticated && user?.role !== "admin") {
    return <AccessDenied required={["admin"]} />
  }

  const filteredVisitors = pendingVisitors.filter(v => 
    v.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    v.hostName.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="min-h-screen bg-background p-6 md:p-12">
      <div className="max-w-6xl mx-auto space-y-8">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Shield className="w-8 h-8 text-primary" />
              Admin Dashboard
            </h1>
            <p className="text-muted-foreground mt-1">Manage visitor requests and system security.</p>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm" onClick={fetchPending} disabled={isLoading}>
              <RefreshCcw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input 
                placeholder="Search requests..." 
                className="pl-9 bg-card w-64" 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main List */}
          <div className="lg:col-span-2 space-y-6">
            <Card className="gradient-border">
              <CardHeader className="flex flex-row items-center justify-between">
                <div>
                  <CardTitle>Pending Approvals</CardTitle>
                  <CardDescription>
                    Review and approve visitor access requests.
                  </CardDescription>
                </div>
                <Badge variant="secondary" className="bg-primary/10 text-primary border-primary/20">
                  {filteredVisitors.length} REQUESTS
                </Badge>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-[600px] pr-4">
                  {isLoading ? (
                    <div className="flex flex-col items-center justify-center h-64 space-y-4">
                      <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
                      <p className="text-sm text-muted-foreground">Loading requests...</p>
                    </div>
                  ) : filteredVisitors.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-64 text-center space-y-4 border-2 border-dashed rounded-xl">
                      <div className="p-4 rounded-full bg-muted">
                        <Users className="w-8 h-8 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="font-medium">No pending requests</p>
                        <p className="text-sm text-muted-foreground">All visitor requests have been processed.</p>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredVisitors.map((visitor) => {
                        const vid = visitor.visitorId || visitor.visitor_id || visitor.id
                        return (
                        <Card key={vid} className="bg-secondary/20 hover:bg-secondary/30 transition-colors border-border/50">
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between gap-4">
                              <div className="flex items-start gap-4">
                                <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-border flex-shrink-0">
                                  <img src={visitor.photo} alt={visitor.name} className="w-full h-full object-cover" />
                                </div>
                                <div>
                                  <h3 className="font-bold">{visitor.name}</h3>
                                  <div className="flex items-center gap-2 mt-1">
                                    <Badge variant="outline" className="text-[10px] py-0 h-4">
                                      {visitor.hostDepartment || visitor.host_department}
                                    </Badge>
                                    <span className="text-[10px] text-muted-foreground uppercase tracking-wider">
                                      HOST: {visitor.hostName || visitor.host_name}
                                    </span>
                                  </div>
                                  <p className="text-sm text-muted-foreground mt-2 line-clamp-2 italic">
                                    "{visitor.visitPurpose || visitor.visit_purpose}"
                                  </p>
                                  <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                                    <div className="flex items-center gap-1">
                                      <Clock className="w-3 h-3" />
                                      {visitor.maxDuration || visitor.max_duration} Hours
                                    </div>
                                    <div className="flex items-center gap-1">
                                      <RefreshCcw className="w-3 h-3" />
                                      {new Date(visitor.createdAt || visitor.created_at).toLocaleDateString()}
                                    </div>
                                  </div>
                                </div>
                              </div>
                              <div className="flex flex-col gap-2 shrink-0">
                                <Button 
                                  size="sm" 
                                  className="bg-accent hover:bg-accent/90"
                                  onClick={() => handleApprove(vid)}
                                  disabled={actioningId === vid}
                                >
                                  <CheckCircle className="w-4 h-4 mr-2" />
                                  Approve
                                </Button>
                                <Button 
                                  size="sm" 
                                  variant="outline" 
                                  className="text-destructive hover:bg-destructive/10"
                                  onClick={() => handleDecline(vid)}
                                  disabled={actioningId === vid}
                                >
                                  <XCircle className="w-4 h-4 mr-2" />
                                  Decline
                                </Button>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                        )
                      })}
                    </div>
                  )}
                </ScrollArea>
              </CardContent>
            </Card>
          </div>

          {/* Side Info */}
          <div className="space-y-6">
            <Card className="bg-card/50">
              <CardHeader>
                <CardTitle className="text-sm uppercase tracking-wider text-muted-foreground">Security Overview</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/30">
                  <span className="text-sm">Active Visitors</span>
                  <span className="font-bold text-accent">12</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/30">
                  <span className="text-sm">Pending Requests</span>
                  <span className="font-bold text-primary">{pendingVisitors.length}</span>
                </div>
                <div className="flex justify-between items-center p-3 rounded-lg bg-secondary/30 text-destructive">
                  <span className="text-sm">Security Alerts</span>
                  <span className="font-bold">2</span>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-primary/5 border-primary/20">
              <CardContent className="p-6">
                <div className="flex items-start gap-3">
                  <Shield className="w-5 h-5 text-primary mt-1" />
                  <div>
                    <h4 className="font-bold text-sm">Approval Guidelines</h4>
                    <ul className="text-xs text-muted-foreground mt-2 space-y-2 list-disc pl-4">
                      <li>Verify host relationship before approval.</li>
                      <li>Check purpose for security compliance.</li>
                      <li>Review photo for clear facial recognition.</li>
                      <li>Report suspicious patterns immediately.</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
