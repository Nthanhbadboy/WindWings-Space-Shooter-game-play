class_name MonetizationProvider
extends Node

signal provider_initialized(provider_id: String, available: bool, message: String)
signal products_query_finished(provider_id: String, products: Array, success: bool, message: String)
signal purchase_finished(
	provider_id: String, product_id: String, success: bool, transaction_id: String, message: String
)
signal restore_finished(provider_id: String, success: bool, product_ids: Array, message: String)
signal rewarded_ad_finished(
	provider_id: String, placement_id: String, success: bool, reward_granted: bool, message: String
)

var provider_id := "base"
var display_name := "Base provider"
var advert_api_present := false
var _catalog_product_ids: Array = []


func is_available() -> bool:
	return false


func configure_catalog(product_ids: Array) -> void:
	_catalog_product_ids = product_ids.duplicate()


func initialize() -> void:
	provider_initialized.emit(provider_id, false, "No store SDK is attached.")


func query_products(_product_ids: Array = []) -> void:
	products_query_finished.emit(
		provider_id, [], false, "No product service is configured; catalog prices are UNKNOWN."
	)


func purchase(product_id: String) -> void:
	purchase_finished.emit(
		provider_id,
		product_id,
		false,
		"",
		"No transaction was created; provider is an interface-only base."
	)


func restore_purchases() -> void:
	restore_finished.emit(provider_id, false, [], "No receipt/entitlement service is configured.")


func show_rewarded_ad(placement_id: String) -> void:
	rewarded_ad_finished.emit(
		provider_id, placement_id, false, false, "No ad SDK is configured; no reward was granted."
	)
