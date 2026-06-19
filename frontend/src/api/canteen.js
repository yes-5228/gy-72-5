import { api } from './client'

export function fetchCategories() {
  return api.get('/categories/')
}

export function fetchDishes(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, value)
    }
  })
  const suffix = search.toString() ? `?${search}` : ''
  return api.get(`/dishes/${suffix}`)
}

export function createOrder(payload) {
  return api.post('/orders/', payload)
}

export function analyzeNutrition(items) {
  if (items.length > 0 && typeof items[0] === 'object') {
    const payload = items.map((item) => ({
      dish_id: item.dish_id ?? item.dish?.id ?? item.id,
      quantity: item.quantity ?? 1,
    }))
    return api.post('/nutrition/analyze/', { items: payload })
  }
  return api.post('/nutrition/analyze/', { dish_ids: items })
}

export function fetchDeliveries() {
  return api.get('/deliveries/?ordering=estimated_arrival')
}

export function updateDelivery(id, payload) {
  return api.patch(`/deliveries/${id}/`, payload)
}

export function fetchReviews() {
  return api.get('/reviews/?ordering=-created_at')
}

export function createReview(payload) {
  return api.post('/reviews/', payload)
}
