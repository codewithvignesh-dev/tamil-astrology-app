document.addEventListener("DOMContentLoaded", function () {

    const checkbox = document.getElementById("additional_details");
    const section = document.getElementById("additional-details-section");

    const addButton = document.getElementById("add-family-member");
    const membersContainer = document.getElementById("family-members");


    checkbox.addEventListener("change", function () {

        if (this.checked) {
            section.classList.remove("hidden");
        } else {
            section.classList.add("hidden");
        }

    });


    addButton.addEventListener("click", function () {

        const member = document.createElement("div");

        member.className =
            "family-member rounded-xl border border-slate-200 bg-white p-4";

        member.innerHTML = `
            <div
                class="grid grid-cols-1 gap-4
                    md:grid-cols-4"
            >

                <div>
                    <label
                        class="mb-2 block text-xs font-semibold
                            text-slate-600"
                    >
                        பெயர்
                    </label>

                    <input
                        type="text"
                        name="family_name[]"
                        class="w-full rounded-lg
                            border border-slate-200
                            bg-slate-50 px-3 py-2.5
                            text-sm text-slate-900
                            outline-none
                            focus:border-violet-500
                            focus:bg-white"
                        placeholder="பெயர்"
                    >
                </div>


                <div>
                    <label
                        class="mb-2 block text-xs font-semibold
                            text-slate-600"
                    >
                        உறவு
                    </label>

                    <select
                        name="family_relation[]"
                        class="w-full rounded-lg
                            border border-slate-200
                            bg-slate-50 px-3 py-2.5
                            text-sm text-slate-900
                            outline-none
                            focus:border-violet-500
                            focus:bg-white"
                    >
                        <option value="">உறவை தேர்ந்தெடுக்கவும்</option>
                        <option value="Father">தந்தை</option>
                        <option value="Mother">தாய்</option>
                        <option value="Elder Brother">மூத்த சகோதரர்</option>
                        <option value="Younger Brother">இளைய சகோதரர்</option>
                        <option value="Elder Sister">மூத்த சகோதரி</option>
                        <option value="Younger Sister">இளைய சகோதரி</option>
                    </select>
                </div>

                <div>
                    <label
                        class="mb-2 block text-xs font-semibold
                            text-slate-600"
                    >
                        வயது
                    </label>

                    <input
                        type="number"
                        name="family_age[]"
                        min="0"
                        max="150"
                        class="w-full rounded-lg
                            border border-slate-200
                            bg-slate-50 px-3 py-2.5
                            text-sm text-slate-900
                            outline-none
                            focus:border-violet-500
                            focus:bg-white"
                        placeholder="வயது"
                    >
                </div>

                <div>
                    <label
                        class="mb-2 block text-xs font-semibold
                            text-slate-600"
                    >
                        திருமண நிலை
                    </label>

                    <select
                        name="family_marital_status[]"
                        class="w-full rounded-lg
                            border border-slate-200
                            bg-slate-50 px-3 py-2.5
                            text-sm text-slate-900
                            outline-none
                            focus:border-violet-500
                            focus:bg-white"
                    >
                        <option value="">தேர்ந்தெடுக்கவும்</option>
                        <option value="Unmarried">திருமணம் ஆகவில்லை</option>
                        <option value="Married">திருமணமானவர்</option>
                        <option value="Widow">விதவை</option>
                        <option value="Widower">விதவர்</option>
                        <option value="Divorced">விவாகரத்து</option>
                    </select>
                </div>

                <div>
                    <label
                        class="mb-2 block text-xs font-semibold
                            text-slate-600"
                    >
                        வேலை / விவரம்
                    </label>

                    <div class="flex gap-2">

                        <input
                            type="text"
                            name="family_work[]"
                            class="min-w-0 flex-1
                                rounded-lg
                                border border-slate-200
                                bg-slate-50 px-3 py-2.5
                                text-sm text-slate-900
                                outline-none
                                focus:border-violet-500
                                focus:bg-white"
                            placeholder="வேலை / விவரம்"
                        >

                        <button
                            type="button"
                            class="remove-family-member
                                hidden rounded-lg
                                bg-red-50 px-3
                                text-red-600
                                hover:bg-red-100"
                        >
                            ×
                        </button>

                    </div>
                </div>

            </div>
        `;

        membersContainer.appendChild(member);

        updateRemoveButtons();
    });


    function updateRemoveButtons() {

        const members =
            membersContainer.querySelectorAll(".family-member");

        members.forEach(function (member, index) {

            const removeButton =
                member.querySelector(".remove-family-member");

            if (members.length === 1) {
                removeButton.classList.add("hidden");
            } else {
                removeButton.classList.remove("hidden");
            }

        });

    }


    membersContainer.addEventListener("click", function (event) {

        if (
            event.target.classList.contains(
                "remove-family-member"
            )
        ) {

            const member =
                event.target.closest(".family-member");

            member.remove();

            updateRemoveButtons();
        }

    });

});