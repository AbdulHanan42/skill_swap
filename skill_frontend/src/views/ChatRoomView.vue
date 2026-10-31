<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppLayout from '@/components/common/AppLayout.vue'
import ToastMessage from '@/components/common/ToastMessage.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'
import { extractApiError } from '@/api/client'
import { MAX_UPLOAD_BYTES, fetchChatAttachment, uploadChatAttachment } from '@/api/chatApi'
import { useChatRoom } from '@/composables/useChatRoom'
import { useAuthStore } from '@/stores/authStore'
import { useChatStore } from '@/stores/chatStore'
import { formatBytes, isImage, saveBlob } from '@/utils/files'
import { formatChatStamp } from '@/utils/time'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const chatStore = useChatStore()

const search = ref('')
const newMessage = ref('')
const scroller = ref(null)
const composer = ref(null)
const menuOpen = ref(false)
const toast = ref('')
const toastType = ref('success')

const matchId = computed(() => Number(route.params.matchId) || 0)
const selected = computed(() => chatStore.contacts.find((item) => item.id === matchId.value) ?? null)

// A stale link to a room that is not an accepted conversation must not open a socket.
const roomId = computed(() => (selected.value ? matchId.value : 0))

// Mobile shows one panel at a time; key it off the resolved contact so a bad link
// can never hide the conversation list behind an empty chat.
const roomOpen = computed(() => Boolean(selected.value))
const roomMissing = computed(
  () => Boolean(matchId.value) && !selected.value && chatStore.loadedOnce && !chatStore.loading,
)

const { messages, loading, error, connected, disconnected, send, push, connect } = useChatRoom(
  () => roomId.value,
  { onMessage: (id, message) => chatStore.receive(id, message) },
)

const filteredContacts = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return chatStore.contacts
  return chatStore.contacts.filter(
    (contact) =>
      contact.name.toLowerCase().includes(term) ||
      (contact.last_message ?? '').toLowerCase().includes(term),
  )
})

const headerSub = computed(() => {
  const rooms = chatStore.contacts.length
  if (!rooms) return 'Accept a swap request to open your first conversation'
  const unread = chatStore.totalUnread
  return `${rooms} conversation${rooms === 1 ? '' : 's'}${unread ? ` · ${unread} unread` : ''}`
})

const bubbleTime = (iso) =>
  new Date(iso).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' })

function notify(message, type = 'success') {
  toast.value = message
  toastType.value = type
}

function openRoom(contact) {
  menuOpen.value = false
  if (contact.id === matchId.value) return
  router.push({ name: 'chat-room', params: { matchId: contact.id } })
}

function closeRoom() {
  menuOpen.value = false
  router.push({ name: 'chat-room' })
}

function submit() {
  const text = newMessage.value.trim()
  if (!text) return
  if (!send(text)) {
    notify('Not connected yet — tap Reconnect to retry.', 'error')
    return
  }
  newMessage.value = ''
  resizeComposer()
}

function resizeComposer() {
  const node = composer.value
  if (!node) return
  node.style.height = 'auto'
  node.style.height = `${Math.min(node.scrollHeight, 128)}px`
}

const fileInput = ref(null)
const uploading = ref(false)
const pendingName = ref('')
const previews = ref({})

function pickFile() {
  fileInput.value?.click()
}

async function onFilePicked(event) {
  const input = event.target
  const file = input.files?.[0]
  input.value = '' // so choosing the same file again still fires change
  if (!file || !selected.value) return
  if (file.size > MAX_UPLOAD_BYTES) {
    notify(`${file.name} is ${formatBytes(file.size)} — the limit is ${MAX_UPLOAD_BYTES / 1_048_576} MB.`, 'error')
    return
  }
  uploading.value = true
  pendingName.value = file.name
  try {
    const message = await uploadChatAttachment(selected.value.id, file, newMessage.value.trim())
    push(message)
    chatStore.receive(selected.value.id, message)
    newMessage.value = ''
    resizeComposer()
  } catch (err) {
    notify(extractApiError(err), 'error')
  } finally {
    uploading.value = false
    pendingName.value = ''
  }
}

async function loadPreview(message) {
  if (previews.value[message.id]) return
  try {
    const blob = await fetchChatAttachment(message.id)
    previews.value = { ...previews.value, [message.id]: URL.createObjectURL(blob) }
  } catch {
    /* the download button still works without an inline preview */
  }
}

async function download(message) {
  try {
    saveBlob(await fetchChatAttachment(message.id), message.attachment.filename)
  } catch (err) {
    notify(extractApiError(err), 'error')
  }
}

async function scrollToBottom() {
  await nextTick()
  const node = scroller.value
  if (node) node.scrollTop = node.scrollHeight
}

watch(newMessage, resizeComposer)

watch(matchId, () => {
  menuOpen.value = false
  newMessage.value = ''
  scrollToBottom()
})

// The contact only exists once the sidebar has loaded, so reading is credited there.
watch(selected, (contact) => {
  if (contact) chatStore.markRead(contact.id)
}, { immediate: true })

watch(() => [messages.value.length, loading.value], scrollToBottom)

watch(
  messages,
  (list) => {
    for (const message of list) {
      if (isImage(message.attachment)) loadPreview(message)
    }
  },
  { immediate: true },
)

function dismissMenu(event) {
  if (!event.target.closest('[data-chat-menu]')) menuOpen.value = false
}

onMounted(() => {
  // AppLayout owns the first load; this only covers a direct mount of the view.
  if (!chatStore.loadedOnce && !chatStore.loading) chatStore.load()
  document.addEventListener('click', dismissMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', dismissMenu)
  for (const url of Object.values(previews.value)) URL.revokeObjectURL(url)
})
</script>

<template>
  <AppLayout>
    <template #header-sub>
      <p class="mt-1 text-xs text-[var(--text-secondary)]">{{ headerSub }}</p>
    </template>

    <div class="flex h-[calc(100vh-17.5rem)] min-h-[22rem] flex-col overflow-hidden rounded-xl border border-[var(--border-color)] bg-[var(--bg-surface)] shadow-sm md:h-[calc(100vh-14.5rem)] lg:h-[calc(100vh-15rem)]">
      <div class="flex min-h-0 flex-1">
        <!-- Left panel: conversations -->
        <aside
          class="min-w-0 flex-col border-r border-[var(--border-color)] bg-[var(--bg-surface)] md:flex md:w-[320px] lg:w-[360px]"
          :class="roomOpen ? 'hidden w-full' : 'flex w-full md:w-[320px] lg:w-[360px]'"
        >
          <div class="sticky top-0 z-10 shrink-0 border-b border-[var(--border-color)] bg-[var(--bg-surface)] p-3">
            <div class="relative">
              <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--text-secondary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
              <input
                v-model="search"
                type="search"
                placeholder="Search conversations..."
                class="w-full rounded-lg border border-[var(--border-color)] bg-[var(--bg-base)] py-2 pl-9 pr-3 text-sm outline-none transition focus:border-[var(--accent-primary)]"
              />
            </div>
          </div>

          <div class="min-h-0 flex-1 overflow-y-auto">
            <div v-if="chatStore.loading && !chatStore.loadedOnce" class="space-y-3 p-3">
              <div v-for="n in 4" :key="n" class="flex items-center gap-3">
                <div class="h-11 w-11 shrink-0 animate-pulse rounded-full bg-[var(--border-color)]"></div>
                <div class="flex-1 space-y-2">
                  <div class="h-3 w-1/2 animate-pulse rounded bg-[var(--border-color)]"></div>
                  <div class="h-3 w-3/4 animate-pulse rounded bg-[var(--border-color)]"></div>
                </div>
              </div>
            </div>

            <div v-else-if="chatStore.error" class="m-3 rounded-lg border border-[var(--danger-border)] bg-[var(--danger-bg)] px-3 py-2.5 text-xs font-semibold text-[var(--danger-text)]">
              {{ chatStore.error }}
              <button type="button" class="ml-2 underline" @click="chatStore.load()">Retry</button>
            </div>

            <template v-else>
              <button
                v-for="contact in filteredContacts"
                :key="contact.id"
                type="button"
                class="flex w-full items-center gap-3 border-l-4 p-3 text-left transition"
                :class="contact.id === matchId
                  ? 'border-[var(--accent-primary)] bg-[var(--bg-base)]'
                  : 'border-transparent hover:bg-[var(--bg-base)]'"
                @click="openRoom(contact)"
              >
                <div class="relative shrink-0">
                  <UserAvatar :name="contact.name" :src="contact.avatar" size="md" />
                  <span
                    v-if="contact.online"
                    class="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full bg-[var(--success-text)] ring-2 ring-[var(--bg-surface)]"
                  ></span>
                </div>

                <div class="min-w-0 flex-1">
                  <div class="flex items-baseline justify-between gap-2">
                    <h3 class="truncate text-sm font-bold">{{ contact.name }}</h3>
                    <span class="shrink-0 text-[11px] text-[var(--text-secondary)]">{{ formatChatStamp(contact.last_message_at) }}</span>
                  </div>
                  <div class="mt-0.5 flex items-center justify-between gap-2">
                    <p class="min-w-0 flex-1 truncate text-xs text-[var(--text-secondary)]">
                      <span v-if="contact.last_message_mine" class="text-[var(--text-primary)]">You: </span>{{ contact.last_message ?? 'No messages yet — say hello' }}
                    </p>
                    <span
                      v-if="contact.unread_count"
                      class="flex h-5 min-w-5 shrink-0 items-center justify-center rounded-full bg-[var(--success-bg)] px-1.5 text-[10px] font-bold text-[var(--success-text)]"
                    >{{ contact.unread_count }}</span>
                  </div>
                </div>
              </button>

              <div v-if="!filteredContacts.length" class="px-6 py-12 text-center">
                <p class="text-sm font-bold">{{ search ? 'No conversations found' : 'No conversations yet' }}</p>
                <p class="mt-1 text-xs text-[var(--text-secondary)]">
                  {{ search ? 'Try a different name or message.' : 'Accepted swap requests appear here.' }}
                </p>
              </div>
            </template>
          </div>
        </aside>

        <!-- Right panel: active room -->
        <section class="min-w-0 flex-1 flex-col bg-[var(--bg-base)]" :class="roomOpen ? 'flex' : 'hidden md:flex'">
          <template v-if="selected">
            <header class="flex shrink-0 items-center gap-3 border-b border-[var(--border-color)] bg-[var(--bg-surface)] px-3 py-2.5 lg:px-4">
              <button
                type="button"
                class="rounded-lg p-2 text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)] md:hidden"
                title="Back to conversations"
                @click="closeRoom"
              >
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>
              </button>

              <UserAvatar :name="selected.name" :src="selected.avatar" size="header" />

              <div class="min-w-0 flex-1">
                <h2 class="truncate text-sm font-bold">{{ selected.name }}</h2>
                <p class="flex items-center gap-1.5 text-[11px]" :class="selected.online ? 'text-[var(--success-text)]' : 'text-[var(--text-secondary)]'">
                  <span class="h-1.5 w-1.5 rounded-full" :class="selected.online ? 'animate-pulse bg-[var(--success-text)]' : 'bg-[var(--text-secondary)]'"></span>
                  {{ selected.online ? 'Online' : 'Offline' }}
                  <span v-if="selected.designation" class="truncate opacity-70">· {{ selected.designation }}</span>
                </p>
              </div>

              <div class="flex shrink-0 items-center gap-1">
                <button type="button" class="rounded-lg p-2 text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]" title="Audio call" @click="notify('Voice calls are not part of this build yet — agree a time in chat.', 'info')">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.79 19.79 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.9.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/></svg>
                </button>
                <button type="button" class="rounded-lg p-2 text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]" title="Video call" @click="notify('Video calls are not part of this build yet — agree a time in chat.', 'info')">
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 13 5.5 3.2V7.8L16 11"/><rect x="2" y="6" width="14" height="12" rx="2"/></svg>
                </button>
                <div class="relative" data-chat-menu>
                  <button type="button" class="rounded-lg p-2 text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]" title="Chat options" :aria-expanded="menuOpen" @click="menuOpen = !menuOpen">
                    <svg class="h-4 w-4" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="12" cy="19" r="1.6"/></svg>
                  </button>
                  <div v-if="menuOpen" class="absolute right-0 top-10 z-30 w-44 overflow-hidden rounded-lg border border-[var(--border-color)] bg-[var(--bg-surface)] py-1 shadow-lg">
                    <button type="button" class="block w-full px-3 py-2 text-left text-xs font-medium text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]" @click="chatStore.markRead(selected.id); menuOpen = false">Mark as read</button>
                    <button type="button" class="block w-full px-3 py-2 text-left text-xs font-medium text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)]" @click="chatStore.refresh(); menuOpen = false">Refresh conversations</button>
                    <button type="button" class="block w-full px-3 py-2 text-left text-xs font-medium text-[var(--danger-text)] transition hover:bg-[var(--danger-bg)]" @click="closeRoom">Close chat</button>
                  </div>
                </div>
              </div>
            </header>

            <div v-if="error" class="flex shrink-0 items-center justify-between gap-3 border-b border-[var(--danger-border)] bg-[var(--danger-bg)] px-4 py-2 text-xs font-semibold text-[var(--danger-text)]">
              {{ error }}
              <button type="button" class="underline" @click="connect()">Reconnect</button>
            </div>
            <div v-else-if="disconnected && !connected" class="flex shrink-0 items-center justify-between gap-3 border-b border-[var(--border-color)] bg-[var(--warning-bg)] px-4 py-2 text-xs font-semibold text-[var(--warning-text)]">
              Connection closed.
              <button type="button" class="underline" @click="connect()">Reconnect</button>
            </div>

            <div ref="scroller" class="min-h-0 flex-1 space-y-3 overflow-y-auto p-4">
              <div v-if="loading" class="space-y-3">
                <div v-for="n in 3" :key="n" class="h-11 w-2/3 animate-pulse rounded-xl bg-[var(--border-color)]" :class="n % 2 ? '' : 'ml-auto'"></div>
              </div>

              <div v-else-if="!messages.length" class="flex h-full flex-col items-center justify-center text-center">
                <div class="flex h-12 w-12 items-center justify-center rounded-full bg-[var(--accent-primary)]/10">
                  <svg class="h-6 w-6 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                </div>
                <p class="mt-3 text-sm font-bold">Say hello to {{ selected.name }}</p>
                <p class="mt-1 max-w-xs text-xs text-[var(--text-secondary)]">Agree what each of you teaches, then schedule the first session.</p>
              </div>

              <div
                v-for="message in messages"
                :key="message.id"
                class="flex"
                :class="message.sender_id === auth.user?.id ? 'justify-end' : 'justify-start'"
              >
                <div
                  class="max-w-[70%] break-words p-3 text-sm leading-relaxed shadow-sm"
                  :class="message.sender_id === auth.user?.id
                    ? 'rounded-bl-xl rounded-tl-xl rounded-tr-xl bg-[var(--accent-primary)] text-white'
                    : 'rounded-br-xl rounded-tr-xl rounded-tl-xl border border-[var(--border-color)] bg-[var(--bg-base)] text-[var(--text-primary)]'"
                >
                  <div
                    v-if="message.attachment"
                    class="mb-2 overflow-hidden rounded-lg border"
                    :class="message.sender_id === auth.user?.id ? 'border-white/30' : 'border-[var(--border-color)]'"
                  >
                    <img
                      v-if="isImage(message.attachment) && previews[message.id]"
                      :src="previews[message.id]"
                      :alt="message.attachment.filename"
                      class="block max-h-60 w-full bg-[var(--bg-surface)] object-contain"
                    />
                    <button
                      type="button"
                      class="flex w-full items-center gap-2 px-2.5 py-2 text-left transition"
                      :class="message.sender_id === auth.user?.id ? 'hover:bg-white/10' : 'hover:bg-[var(--bg-surface)]'"
                      :title="`Download ${message.attachment.filename}`"
                      @click="download(message)"
                    >
                      <svg class="h-5 w-5 shrink-0 opacity-80" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/></svg>
                      <span class="min-w-0 flex-1 truncate text-xs font-semibold">{{ message.attachment.filename }}</span>
                      <span class="shrink-0 text-[10px] opacity-75">{{ formatBytes(message.attachment.size) }}</span>
                    </button>
                  </div>

                  <p v-if="message.content" class="whitespace-pre-wrap">{{ message.content }}</p>
                  <span
                    class="mt-1 block text-right text-[10px]"
                    :class="message.sender_id === auth.user?.id ? 'text-white/70' : 'text-[var(--text-secondary)]'"
                  >{{ bubbleTime(message.sent_at) }}</span>
                </div>
              </div>
            </div>

            <div v-if="uploading" class="flex shrink-0 items-center gap-2 border-t border-[var(--border-color)] bg-[var(--bg-surface)] px-4 py-2 text-xs font-semibold text-[var(--text-secondary)]">
              <svg class="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12a9 9 0 1 1-6.216-8.56"/></svg>
              <span class="truncate">Uploading {{ pendingName }}…</span>
            </div>

            <form class="flex shrink-0 items-center gap-3 border-t border-[var(--border-color)] bg-[var(--bg-surface)] p-4" @submit.prevent="submit">
              <input ref="fileInput" type="file" class="hidden" :disabled="uploading" @change="onFilePicked" />
              <button
                type="button"
                class="shrink-0 rounded-lg p-2 text-[var(--text-secondary)] transition hover:bg-[var(--bg-base)] hover:text-[var(--text-primary)] disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="uploading"
                :title="`Attach a file (up to ${MAX_UPLOAD_BYTES / 1048576} MB)`"
                @click="pickFile"
              >
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a3 3 0 0 1 4.24 4.24l-9.2 9.19a1.5 1.5 0 0 1-2.12-2.12l8.49-8.48"/></svg>
              </button>

              <textarea
                ref="composer"
                v-model="newMessage"
                rows="1"
                maxlength="4000"
                :disabled="!connected"
                :placeholder="connected ? 'Type a message...' : 'Waiting for the connection...'"
                class="max-h-32 min-h-[2.75rem] w-full resize-none rounded-xl border border-[var(--border-color)] bg-[var(--bg-base)] px-4 py-2.5 text-sm outline-none transition focus:border-[var(--accent-primary)] disabled:cursor-not-allowed disabled:opacity-60"
                @keydown.enter.exact.prevent="submit"
              ></textarea>

              <button
                type="submit"
                :disabled="!connected || !newMessage.trim()"
                title="Send message"
                class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[var(--accent-primary)] text-white transition hover:bg-[var(--accent-hover)] disabled:cursor-not-allowed disabled:opacity-50"
              >
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 2 11 13"/><path d="M22 2 15 22l-4-9-9-4Z"/></svg>
              </button>
            </form>
          </template>

          <!-- No room selected -->
          <div v-else class="flex h-full flex-col items-center justify-center px-6 text-center">
            <div class="flex h-16 w-16 items-center justify-center rounded-full bg-[var(--accent-primary)]/10">
              <svg class="h-8 w-8 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </div>
            <h3 class="mt-4 text-lg font-bold">{{ roomMissing ? 'Chat room unavailable' : 'No chat room open' }}</h3>
            <p class="mt-1 max-w-sm text-sm text-[var(--text-secondary)]">
              {{ roomMissing
                ? 'This conversation is not open to you — the swap request behind it may have been declined or removed.'
                : chatStore.loadedOnce && !chatStore.contacts.length
                  ? 'Chat rooms unlock as soon as a swap request is accepted.'
                  : 'Pick a connected partner on the left to start the conversation.' }}
            </p>
            <RouterLink
              :to="{ name: 'swap-requests' }"
              class="mt-5 rounded-lg bg-[var(--accent-primary)] px-4 py-2 text-sm font-bold text-white transition hover:bg-[var(--accent-hover)]"
            >Go to Swap Requests</RouterLink>
          </div>
        </section>
      </div>
    </div>

    <div class="pointer-events-none fixed bottom-6 right-6 z-40 w-80 max-w-[calc(100vw-3rem)]">
      <ToastMessage :message="toast" :type="toastType" @dismiss="toast = ''" />
    </div>
  </AppLayout>
</template>
