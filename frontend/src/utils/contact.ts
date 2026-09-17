export interface ContactDraft {
  name: string
  email: string
  subject: string
  message: string
}
export function contactBody(draft: ContactDraft) {
  return [
    draft.message.trim(),
    '',
    'Имя: ' + draft.name.trim(),
    'Email для ответа: ' + draft.email.trim(),
  ].join('\n')
}
export function contactMailto(draft: ContactDraft) {
  return (
    'mailto:info@expertpolymer.ru?subject=' +
    encodeURIComponent(draft.subject.trim()) +
    '&body=' +
    encodeURIComponent(contactBody(draft))
  )
}
