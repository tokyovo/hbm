from django.views.generic import TemplateView
from django.shortcuts import render
from .forms import CollectionSelectForm
from .models import WixProduct, Collection

class WixProductListView(TemplateView):
    template_name = 'agent/wixproduct_list.html'

    def get(self, request, *args, **kwargs):
        form = CollectionSelectForm()
        return self.render_to_response({'form': form})

    def post(self, request, *args, **kwargs):
        form = CollectionSelectForm(request.POST)
        if form.is_valid():
            collection = form.cleaned_data['collection']
            wix_products = WixProduct.objects.filter(collections=collection)

            # Pass the selected collection and products back to the template
            return self.render_to_response({
                'form': form,
                'wix_products': wix_products,
                'collection': collection
            })

        # If form is not valid, render the form again
        return self.render_to_response({'form': form})
