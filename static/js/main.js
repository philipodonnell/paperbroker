(function() {


    var api = {}


    api.openAccount = function openAccount(done) {
        jQuery.get('/accounts/create', function (account){
        	console.log('api.openAccount', account);
            sessionStorage.setItem('accountId', account.account_id);
            return done && done(null, account)
        });
    }

    api.getAccount = function getAccount(accountId, done) {
        jQuery.get('/accounts/' + accountId, function (account){
        	console.log('api.getAccount', account);
            return done && done(null, account)
        });
    }

    api.getExpirations = function getExpirations(accountId, underlyingSymbol) {
        jQuery.get('/expirations/' + underlyingSymbol, function(expirations) {
            jQuery('.order-expirations-container').html('');
            console.log('api.getExpirations', accountId, underlyingSymbol, expirations);
            expirations.map(function(expiration) {
                jQuery('<a class="label label-default order-expiration"></a>')
                    .html(expiration)
                    .appendTo('.order-expirations-container')
            });
        });
    }

    api.getPrices = function(accountId, underlyingSymbol, expirationDate) {
        jQuery.get('/quotes/' + underlyingSymbol + "/options/" + expirationDate, null, function(prices) {
            jQuery('.order-option-prices-container').html('');
            console.log('api.getPrices', accountId, underlyingSymbol, expirationDate, prices);
            prices.map(function(price) {
                jQuery('<a class="label label-default order-option-price"></a>')
                    .html(price.asset.symbol + ' - ' + price.price.toFixed(2))
                    .data("quote", price)
                    .appendTo('.order-option-prices-container')
                jQuery('<a> </a>')
                    .appendTo('.order-option-prices-container')
            });
        }, 'json');
    }


    api.simulateOrder = function simulateOrder(accountId, order, done) {
    	jQuery.get('/accounts/' + accountId + "/orders/create?simulate=true&" + $.param(order), function(account) {
    		console.log('api.simulateOrder', order, account)
            return done && done(null, account)
        });
    }

    api.enterOrder = function simulateOrder(accountId, order, done) {
    	jQuery.get('/accounts/' + accountId + "/orders/create?&" + $.param(order), function(account) {
    		console.log('api.enterOrder', order, account)
            return done && done(null, account)
        });
    }






    var addSymbolToOrder = function addSymbolToOrder(quote) {
    	$template = jQuery(jQuery('tr.legT')["0"].outerHTML);
    	$template.removeClass('legT');
    	$template.removeClass('hidden');
    	$template.addClass('leg');
        $template.find('.order-leg-symbol').html(quote.asset.symbol);
        $template.find('.order-leg-price').html(quote.price.toFixed(2));
    	$template.find('.order-leg-clear').click(function() {
    		$template.detach()
    	});
    	$template.appendTo('.current-leg-container');
    	refreshCurrentOrder()
    }

    var addPositionToScreen = function addPositionToScreen(position) {
    	$template = jQuery(jQuery('tr.positionT')["0"].outerHTML);
    	$template.removeClass('positionT');
    	$template.removeClass('hidden');
    	$template.addClass('position');
        $template.find('.position-quantity').html(position.quantity);
        $template.find('.position-cost-basis').html(position.cost_basis);
        $template.find('.position-symbol').html(position.asset.symbol);
        $template.find('.position-price').html(position.quote.price.toFixed(2));
    	$template.appendTo('.positions-container');
    }


    var buildOrderFromPage = function buildOrderFromPage() {
    	order = { legs : [] }

    	$('tr.leg').each(function() {
    		e = $(this)
    		var leg = {}
    		leg.quantity = e.find('.order-leg-quantity').val()
    		leg.order_type = e.find('.order-leg-side').find(':selected').val()
    		leg.asset = e.find('.order-leg-symbol').text()
    		order.legs.push(leg)
    	});

    	return order;

    }

    var refreshCurrentOrder = function refreshCurrentOrder() {
    	order = buildOrderFromPage()
    	if (order.legs.length > 0) {
            refreshOrOpenAccount(null, function(err, account1) {
	    		api.simulateOrder(account1.account_id, order, function(err, resp) {
	    		   $('.order-simulation .cash-before').html(resp.account0.cash.toFixed(2));
	    		   $('.order-simulation .cash-after').html(resp.account1.cash.toFixed(2));
	    		   $('.order-simulation .margin-before').html(resp.account0.maintenance_margin ? resp.account0.maintenance_margin.toFixed(2) : '0');
	    		   $('.order-simulation .margin-after').html(resp.account1.maintenance_margin ? resp.account1.maintenance_margin.toFixed(2) : '0');
	    		});
    		});
    	}
    }



    var refreshOrOpenAccount = function refreshOrOpenAccount(opened, done) {


        function qs(key) {
            key = key.replace(/[*+?^$.\[\]{}()|\\\/]/g, "\\$&"); // escape RegEx meta chars
            var match = location.search.match(new RegExp("[?&]"+key+"=([^&]+)(&|$)"));
            return match && decodeURIComponent(match[1].replace(/\+/g, " "));
        }

        function getParameterByName(name) {
            var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
            return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
        }

        accountId = qs('accountId') || getParameterByName('accountId') || sessionStorage.getItem('accountId') 
        if (!accountId) return api.openAccount(function(){ refreshOrOpenAccount(true, done); });

        sessionStorage.setItem('accountId', accountId)

        api.getAccount(accountId, function(err, account){ 
           
            if (opened) $('.new-account-warning').removeClass('hidden');

            $('.new-account-warning').find('.account-access-url').html(window.location.protocol + "//" + window.location.host + "?accountId=" + account.account_id)
            $('.account .account-id').html(account.account_id)
            $('.account .cash').html(account.cash.toFixed(2))

			$('.positions-container .position').html('');
			account.positions.map(addPositionToScreen);


            // store the account also on the account
            $('.account').data('account', account)

	        return done && done(null, account)
    
        });
                
    }






    jQuery(function() {

        
        refreshOrOpenAccount()

        jQuery('input.order-underlying-symbol').keyup(function() {
            api.getExpirations(null, this.value.toUpperCase())
        });

        jQuery('.order-expirations-container').click(function(e) {
            api.getPrices(null, jQuery('input.order-underlying-symbol').val(), e.target.innerText)
        });


        jQuery('.order-option-prices-container').click(function(e) {
        	addSymbolToOrder($(e.target).data('quote'));
        });



		jQuery('input.order-underlying-symbol').val('AAPL')
        api.getExpirations(null, 'AAPL')

       	jQuery('.order-submit').click(function(){

			order = buildOrderFromPage()
			if (order.legs.length > 0) {
				refreshOrOpenAccount(null, function(err, account1) {
					api.enterOrder(account1.account_id, order, function(err, resp) {
			    		refreshOrOpenAccount()
					});
				});
			}

        	

        });

		jQuery('.order-leg-quantity').keyup(function() {
			refreshCurrentOrder()
		});

		jQuery('.order-leg-side').change(function() {
			refreshCurrentOrder()
		});


		$('body').on('change', '.order-leg-side', function() {
			refreshCurrentOrder()
			})

        jQuery("a.order-expiration").click(function(e) {

            // clicked an order expiration link

            // clear out all the options from the ui and get different prices


        });


    })





































})()