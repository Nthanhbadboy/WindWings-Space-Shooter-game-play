class_name MonetizationService
extends Node

signal provider_selected(provider_id: String, display_name: String)
signal provider_status(provider_id: String, available: bool, message: String)
signal product_query_result(provider_id: String, products: Array, success: bool, message: String)
signal purchase_result(
	provider_id: String, product_id: String, success: bool, transaction_id: String, message: String
)
signal restore_result(provider_id: String, success: bool, product_ids: Array, message: String)
signal rewarded_ad_result(
	provider_id: String, placement_id: String, success: bool, reward_granted: bool, message: String
)

const PROVIDER_ORDER := ["amazon_iap", "hms_iap_ads", "windows_commerce"]

var _providers: Dictionary = {}
var _product_ids: Array = []
var _active_provider_id := ""


func _ready() -> void:
	_register_provider(AmazonIapStub.new())
	_register_provider(HmsIapAdsStub.new())
	_register_provider(WindowsCommerceStub.new())


func configure(product_document: Dictionary, config: Dictionary) -> void:
	_product_ids.clear()
	var groups: Dictionary = product_document.get("groups", {})
	for group_name in ["ConsumableProducts", "NonConsumableProducts"]:
		for product_value: Variant in groups.get(group_name, []):
			var product_id := str(product_value)
			if not product_id.is_empty() and not _product_ids.has(product_id):
				_product_ids.append(product_id)
	if _product_ids.size() != int(product_document.get("count", _product_ids.size())):
		push_warning("IAP catalog count differs from the decoded product manifest.")
	for provider: MonetizationProvider in _providers.values():
		provider.configure_catalog(_product_ids)
	var default_provider := str(config.get("default_provider_id", ""))
	if not default_provider.is_empty():
		select_provider(default_provider)


func get_provider_summaries() -> Array:
	var summaries: Array = []
	for id in PROVIDER_ORDER:
		if not _providers.has(id):
			continue
		var provider: MonetizationProvider = _providers[id]
		summaries.append(
			{
				"provider_id": provider.provider_id,
				"display_name": provider.display_name,
				"available": provider.is_available(),
				"advert_api_present": provider.advert_api_present,
				"implementation": "STUB_ONLY"
			}
		)
	return summaries


func get_product_ids() -> Array:
	return _product_ids.duplicate()


func select_provider(provider_id: String) -> bool:
	if not _providers.has(provider_id):
		provider_status.emit(provider_id, false, "Unknown provider ID; no adapter was selected.")
		return false
	_active_provider_id = provider_id
	var provider: MonetizationProvider = _providers[provider_id]
	provider_selected.emit(provider_id, provider.display_name)
	provider.configure_catalog(_product_ids)
	provider.initialize()
	provider.query_products(_product_ids)
	return true


func query_products() -> void:
	var provider := _get_active_provider()
	if provider == null:
		product_query_result.emit("", [], false, "Select one of the local stub providers first.")
		return
	provider.query_products(_product_ids)


func request_purchase(product_id: String) -> void:
	var provider := _get_active_provider()
	if provider == null:
		purchase_result.emit("", product_id, false, "", "Select a local stub provider first.")
		return
	if not _product_ids.has(product_id):
		purchase_result.emit(
			_active_provider_id,
			product_id,
			false,
			"",
			"Product ID is not in the decoded 170-ID catalog."
		)
		return
	provider.purchase(product_id)


func request_restore() -> void:
	var provider := _get_active_provider()
	if provider == null:
		restore_result.emit("", false, [], "Select a local stub provider first.")
		return
	provider.restore_purchases()


func request_rewarded_ad(placement_id: String) -> void:
	var provider := _get_active_provider()
	if provider == null:
		rewarded_ad_result.emit(
			"", placement_id, false, false, "Select a local stub provider first."
		)
		return
	provider.show_rewarded_ad(placement_id)


func _register_provider(provider: MonetizationProvider) -> void:
	provider.provider_initialized.connect(_on_provider_initialized)
	provider.products_query_finished.connect(_on_products_query_finished)
	provider.purchase_finished.connect(_on_purchase_finished)
	provider.restore_finished.connect(_on_restore_finished)
	provider.rewarded_ad_finished.connect(_on_rewarded_ad_finished)
	add_child(provider)
	_providers[provider.provider_id] = provider


func _get_active_provider() -> MonetizationProvider:
	if not _providers.has(_active_provider_id):
		return null
	return _providers[_active_provider_id]


func _on_provider_initialized(provider_id: String, available: bool, message: String) -> void:
	provider_status.emit(provider_id, available, message)


func _on_products_query_finished(
	provider_id: String, products: Array, success: bool, message: String
) -> void:
	product_query_result.emit(provider_id, products, success, message)


func _on_purchase_finished(
	provider_id: String, product_id: String, success: bool, transaction_id: String, message: String
) -> void:
	purchase_result.emit(provider_id, product_id, success, transaction_id, message)


func _on_restore_finished(
	provider_id: String, success: bool, product_ids: Array, message: String
) -> void:
	restore_result.emit(provider_id, success, product_ids, message)


func _on_rewarded_ad_finished(
	provider_id: String, placement_id: String, success: bool, reward_granted: bool, message: String
) -> void:
	rewarded_ad_result.emit(provider_id, placement_id, success, reward_granted, message)
